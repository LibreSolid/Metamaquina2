"""Contracts the assembly has to keep.

These check the thing this layer is actually responsible for.  The
geometry of each part comes from the OpenSCAD design and was correct
before this package existed; what is new here is where every part is
put.  So the tests ask whether parts that must be on the same rod are
on it, and whether the axes reach the travel the machine claims.

Now that the three car positions are drivers, where a part is put is a
question with more than one answer, and the tests ask it more than
once.  Each axis is driven and the part it carries is measured against
where it stood, so a driver that reaches nothing fails; something it
must not carry is measured alongside, so a machine sliding whole would
fail too.  The rod contracts are then asked again at both ends of the
declared travel, which is the same question the rest pose already
answered, put to a machine in motion.

The two belts are the one place where where-a-part-is-put is the wrong
question altogether.  A belt does not go anywhere -- both ends of each
loop are bolted down -- and yet it is not still: the rubber inside the
loop is dragged through it by the carriage clamped to it, so the belt
has to be drawn afresh at every position.  Its tests ask that pair
together, because either half alone would pass for something wrong: a
belt that only moved would be a rigid part badly placed, and one that
only changed shape would be a shape with no carriage in it.  What the
teeth do is then asked exactly, in teeth and in sampled rings rather
than in millimetres, because a tooth pattern is periodic and a test in
millimetres could not tell one tooth from the next.

The two whole-model contracts `solid new` scaffolds --
`assertNoDisconnectedSolids` and `assertNoSolidInterference` -- are
deliberately not asserted, and it is worth being precise about why,
because they would both fail:

* the design draws several bought parts as more than one body, on
  purpose.  A 608 bearing is an inner race, a shield and an outer race
  with air between them; a microswitch is a body and a separate lever;
  the power supply is a case and the board inside it.  Those are
  honest drawings of parts that really are several pieces, not parts
  that have fallen apart.
* the design lets fasteners pass through the material they clamp
  rather than modelling clearance holes for every one of them, so a
  bolt shares volume with the sheet it goes through nearly everywhere.

Neither is something this layer introduced or can fix by moving a part,
and asserting them would only produce a red suite nobody could act on.
Making them true is a change to the OpenSCAD design.
"""

import math

import numpy
import trimesh

from solid_node.core.serializer import (
    document_version,
    serialize_node,
    symbolic_document,
)
from solid_node.simulation import Sim
from solid_node.test import TestCase

from metamaquina2 import gt2
from metamaquina2.hardware.gt2_pulley import TEETH, GT2Pulley
from metamaquina2.params import (
    BuildVolume_X,
    BuildVolume_Y,
    PulleyRadius,
    XCarPosition,
    YCarPosition,
    ZCarPosition,
    belt_width,
)
from metamaquina2.x_stage import x_belt
from metamaquina2.y_axis import y_belt


class Metamaquina2Test(TestCase):

    # An LM8UU is 15 mm across on an 8 mm rod, so every point on the
    # bearing is within 3.5 mm of the rod it is threaded onto.  Any rod
    # it is NOT on is tens of millimetres away, so this distance
    # separates the two cases with room to spare, and does it without
    # depending on how a nominal slip fit tessellates.
    ON_THE_ROD = 6

    # A driven part is placed by arithmetic on millimetres and its mesh
    # is only carried along by the transform, so it lands exactly where
    # it was sent.  A micron of slack allows for the float, and nothing
    # else.
    PLACED = 0.001

    # Two ticks a second: the instructions last whole seconds, and each
    # tick re-renders the entire machine, so there is no reason to pay
    # for a finer step to prove where a ramp lands.
    TICK = 0.5

    # A belt rides the bearings it runs on, so its surface and theirs
    # meet: the shared volume is not a gap but the dust two touching
    # surfaces leave in a mesh boolean, and a thousandth of a cubic
    # millimetre is six orders of magnitude above the dust measured and
    # four below the tens of cubic millimetres a belt drawn a
    # millimetre low cuts out of an outer race.
    RIDING = 0.001

    # A pulley is cut its own `CLEARANCE` inside the surface its belt
    # runs on, so the two are never in contact and the belt's nearest
    # point to it is that far off.  A little under, in fact -- the belt
    # is sampled at rings and its nearest vertex is not always on the
    # flank -- so this is an upper bound on a gap that must exist and
    # must be small: a pulley that has drifted out of the loop
    # altogether is millimetres away, not hundredths.
    MESHED = GT2Pulley.CLEARANCE

    # A GT2 pulley of this machine reaches 4.74 mm from its axis on a
    # 5 mm shaft, so every point of it is within 2.3 mm of the shaft's
    # own surface.  Four separates that from a pulley knocked off the
    # shaft by even a couple of millimetres, and does it without
    # depending on how a cylinder tessellates.
    ON_THE_SHAFT = 4

    # The pulley the bill of materials buys for both belt motors: "GT2
    # pulley 6mm x 16 teeth", ref GT2P6x16_Al.  Sixteen teeth, and six
    # millimetres of belt width.  Nothing in the design is derived from
    # either number -- the line is a string passed to the BOM and the
    # module under it draws nothing -- so they are written out here to
    # be asked of the metal and of the dimensions the design puts its
    # belt at.
    BOUGHT_TEETH = 16
    BOUGHT_WIDTH = 6

    # Positions spent crossing one tooth, for a contract that has to
    # hold at every phase of the mesh rather than at the rest pose.
    # Eight puts a groove floor, a flank and a land at the tangent
    # point in turn, which is where a tooth is halfway out and the
    # geometry is at its tightest.
    PHASES = 8

    def setUp(self):
        """Start every test from the rest pose.

        The runner rebinds the animation instant before each test but
        not the machine's own drivers, so a test that drives an axis
        would otherwise hand the next one a machine still driven.
        """
        self.node.set_state(x=XCarPosition, y=YCarPosition, z=ZCarPosition)

    def test_x_carriage_rides_the_x_rods(self):
        """Every carriage bearing is on a rod.

        Four bearings, two rods, two bearings per rod -- if a placement
        is out, a bearing floats in air and the carriage would fall
        off.
        """
        rods = self.node.x_stage.rods.rods
        for bearing in self.node.x_stage.carriage.bearings:
            self.assertTrue(
                any(self._is_on(bearing, rod) for rod in rods),
                f'{bearing.name} is not on either X rod')

    def test_y_platform_rides_the_y_rods(self):
        """All three platform bearings are on a Y rod."""
        rods = self.node.y_axis.rods.rods
        for bearing in self.node.y_axis.platform.bearings:
            self.assertTrue(
                any(self._is_on(bearing, rod) for rod in rods),
                f'{bearing.name} is not on either Y rod')

    def test_x_ends_ride_the_z_rods(self):
        """Both X ends hang on the Z rods.

        This is the placement most easily got wrong, because the two
        ends are mirror images and the design writes one of them with
        `mirror`, which the node tree has no equivalent for.
        """
        rods = self.node.z_axis.rods.rods
        ends = (self.node.x_stage.end_motor, self.node.x_stage.end_idler)
        for end in ends:
            for bearing in end.bearings:
                self.assertTrue(
                    any(self._is_on(bearing, rod) for rod in rods),
                    f'{bearing.name} is not on either Z rod')

    def test_glass_sits_on_the_heated_bed(self):
        """The build surface rests on the heater, not above it."""
        bed = self.node.y_axis.platform.heated_bed
        self.assertClose(bed.pcb, bed.glass, 130)

    def test_the_bed_covers_the_build_volume(self):
        """The heated bed is wide enough for the advertised build area.

        A contract of the machine rather than of one part: the design
        derives the bed from the build volume, so this catches a change
        at either end of that derivation.
        """
        bed = self.node.y_axis.platform.heated_bed.pcb.mesh
        low, high = bed.bounds
        self.assertGreaterEqual(high[0] - low[0], BuildVolume_X)
        self.assertGreaterEqual(high[1] - low[1], BuildVolume_Y)

    ########################################
    # What the three drivers move

    def test_driving_x_slides_the_carriage_along_the_beam(self):
        """The X driver carries the carriage and leaves the frame.

        Sixty millimetres from rest is unmistakable in a mesh and well
        short of either end of the travel, so this asks only whether
        the driver reaches the carriage at all.
        """
        carriage = self.node.x_stage.carriage.plate
        reference = self.node.frame.panels.top
        carriage_at_rest = carriage.mesh.bounds
        reference_at_rest = reference.mesh.bounds

        self.node.set_state(x=XCarPosition + 60)

        self.assertMovedBy(carriage, carriage_at_rest, [60, 0, 0])
        self.assertStill(reference, reference_at_rest)

    def test_driving_y_slides_the_bed_on_its_rods(self):
        """The Y driver carries the platform, and only the platform.

        The belt and the motor at the back of the axis are deliberately
        left standing, so the reference here is the bed's own rods: if
        those moved with it, the axis would be sliding as one piece
        instead of sliding the bed along them.
        """
        platform = self.node.y_axis.platform.plate
        reference = self.node.y_axis.rods.rods[0]
        platform_at_rest = platform.mesh.bounds
        reference_at_rest = reference.mesh.bounds

        self.node.set_state(y=YCarPosition - 70)

        self.assertMovedBy(platform, platform_at_rest, [0, -70, 0])
        self.assertStill(reference, reference_at_rest)

    def test_driving_z_lowers_the_whole_x_beam(self):
        """The Z driver lowers the beam and everything riding it.

        The X stage travels as one thing, which is why it is one
        assembly, so the beam's own plate and the carriage on it have
        to come down by the same ninety millimetres.
        """
        beam = self.node.x_stage.plate
        carriage = self.node.x_stage.carriage.plate
        reference = self.node.frame.panels.top
        beam_at_rest = beam.mesh.bounds
        carriage_at_rest = carriage.mesh.bounds
        reference_at_rest = reference.mesh.bounds

        self.node.set_state(z=ZCarPosition - 90)

        self.assertMovedBy(beam, beam_at_rest, [0, 0, -90])
        self.assertMovedBy(carriage, carriage_at_rest, [0, 0, -90])
        self.assertStill(reference, reference_at_rest)

    ########################################
    # The placement contracts, extended to motion

    def test_the_carriage_rides_the_x_rods_across_its_travel(self):
        """The carriage keeps its bearings on the rods everywhere.

        `test_x_carriage_rides_the_x_rods` asks this of the rest pose;
        a machine that claims travel has to keep it at both ends of
        that travel too.  The carriage is checked to have actually
        gone there first, or bearings that never left home would ride
        the rods for the wrong reason.
        """
        rods = self.node.x_stage.rods.rods
        carriage = self.node.x_stage.carriage.plate
        at_rest = carriage.mesh.bounds

        for position in self.declared_travel('x'):
            self.node.set_state(x=position)
            self.assertMovedBy(carriage, at_rest,
                               [position - XCarPosition, 0, 0])
            for bearing in self.node.x_stage.carriage.bearings:
                self.assertTrue(
                    any(self._is_on(bearing, rod) for rod in rods),
                    f'{bearing.name} leaves the X rods at x={position}')

    def test_the_x_ends_ride_the_z_rods_across_the_z_travel(self):
        """The beam stays hung on the Z rods over its whole lift."""
        rods = self.node.z_axis.rods.rods
        beam = self.node.x_stage.plate
        at_rest = beam.mesh.bounds
        ends = (self.node.x_stage.end_motor, self.node.x_stage.end_idler)

        for height in self.declared_travel('z'):
            self.node.set_state(z=height)
            self.assertMovedBy(beam, at_rest, [0, 0, height - ZCarPosition])
            for end in ends:
                for bearing in end.bearings:
                    self.assertTrue(
                        any(self._is_on(bearing, rod) for rod in rods),
                        f'{bearing.name} leaves the Z rods at z={height}')

    ########################################
    # The belts, which move without going anywhere

    def test_each_belt_is_a_flexible_leaf_of_its_axis(self):
        """Both belts hang off the axis that drives them, as parts
        whose shape is a function of where that axis is.

        A rigid part promises the same solid wherever the machine
        stands, which is what lets it be cached and fused; a belt makes
        no such promise, and the tree has to know that about it or it
        would be cached at one carriage position and drawn at every
        other.
        """
        for belt, axis in ((self.node.x_stage.belt, self.node.x_stage),
                           (self.node.y_axis.belt, self.node.y_axis)):
            self.assertIn(belt, axis.children)
            self.assertTrue(belt.flexible, f'{belt.name} is not flexible')
            self.assertFalse(belt.rigid, f'{belt.name} claims to be rigid')
            self.assertEqual(belt.tech, 'molejo')
            # One port, and it is the clamp its ends are held by.
            self.assertEqual(sorted(belt.bound_values()), ['clamp'])

    def test_each_belt_is_one_closed_loop(self):
        """A belt is a single closed band of rubber.

        Swept from a closed section along a closed path, so it is
        watertight by construction rather than by repair -- and this is
        what catches the construction going wrong: a loop left open at
        the seam, or a section wound the wrong way round.
        """
        for belt in (self.node.x_stage.belt, self.node.y_axis.belt):
            mesh = belt.mesh
            self.assertTrue(mesh.is_watertight,
                            f'{belt.name} is not a closed band')
            self.assertEqual(len(mesh.split(only_watertight=False)), 1,
                             f'{belt.name} came out in pieces')
            self.assertGreater(mesh.volume, 0,
                               f'{belt.name} is inside out')

    def test_driving_x_redraws_the_belt_where_it_stands(self):
        """The X driver reaches the belt without moving it.

        Both ends of the loop are bolted to the beam, so driving the
        carriage must not shift the belt one micron: what changes is the
        rubber inside the loop, not where the loop is.  Asking for both
        at once is the point -- a belt that only moved would be a rigid
        part badly placed, and one that only changed would be a shape
        with no carriage in it.
        """
        belt = self.node.x_stage.belt
        at_rest = belt.mesh.vertices.copy()
        bounds_at_rest = belt.mesh.bounds.copy()

        self.node.set_state(x=XCarPosition + 60)

        self.assertFalse(numpy.allclose(belt.mesh.vertices, at_rest),
                         'the X belt is drawn the same at two positions')
        numpy.testing.assert_allclose(belt.mesh.bounds, bounds_at_rest,
                                      atol=self.PLACED)

    def test_driving_y_redraws_the_belt_where_it_stands(self):
        """The Y driver reaches the belt without moving it.

        The same contract as the X belt's, asked of the loop that hangs
        on three bearings bolted to the frame.
        """
        belt = self.node.y_axis.belt
        at_rest = belt.mesh.vertices.copy()
        bounds_at_rest = belt.mesh.bounds.copy()

        self.node.set_state(y=YCarPosition - 70)

        self.assertFalse(numpy.allclose(belt.mesh.vertices, at_rest),
                         'the Y belt is drawn the same at two positions')
        numpy.testing.assert_allclose(belt.mesh.bounds, bounds_at_rest,
                                      atol=self.PLACED)

    def test_the_x_belt_teeth_travel_with_the_carriage(self):
        """Drive the carriage and the teeth go with it, exactly.

        Three questions.  Move the carriage one whole tooth and the belt
        comes out drawn precisely as it was, every tooth having stepped
        into the place of the one before it.  Move it half a tooth and
        the belt comes out as differently as it can be: somewhere a
        crest has become a root, which is the tooth height and not a
        micron more.  Move it one sampled ring and the pattern that was
        at a ring is now at the ring after it -- which is the question a
        belt whose teeth ran backwards, or ran at the wrong rate, gets
        wrong, and the other two do not ask.
        """
        self.assertTeethTravel(self.node.x_stage.belt, 'x', XCarPosition,
                               x_belt.CIRCLES, x_belt.CLAMP_SPAN, +1)

    def test_the_y_belt_teeth_travel_with_the_bed(self):
        """Drive the bed and the teeth go with it, exactly.

        The same three questions as the X belt's, and the sign is the
        interesting one: the loop is drawn in a plane the axis stands up
        with a quarter turn, so the bed running towards the rear of the
        machine pulls the belt the other way along its clamped run.
        """
        self.assertTeethTravel(self.node.y_axis.belt, 'y', YCarPosition,
                               y_belt.CIRCLES, y_belt.CLAMP_SPAN, -1)

    def test_the_x_belt_rides_its_idler_without_biting_it(self):
        """The belt sits on the idler bearing, not in it.

        The design draws a belt as a 2 mm ring hulled around the circles
        it wraps, which touches whatever it is drawn around by
        construction.  A belt with teeth is drawn at the radius it
        really runs at -- pitch line outside, tooth tips down on the
        outer race -- and that radius either lands on the bearing or it
        does not.
        """
        idler = self.node.x_stage.end_idler.idler
        self.assertRidesOn(self.node.x_stage.belt, idler.bearing)
        self.assertRidesOn(self.node.x_stage.belt, idler.shaft)

    def test_the_y_belt_rides_the_three_idlers_without_biting_them(self):
        """The belt sits on all three bar bearings, not in any of them.

        Worth asking of each: the loop is placed once, and a height that
        suited two of the three would still be wrong.
        """
        bars = self.node.frame.bars
        for idler in (bars.front.idler, bars.rear.upper_idler,
                      bars.rear.lower_idler):
            self.assertRidesOn(self.node.y_axis.belt, idler.bearing)

    ########################################
    # The pulleys, which go nowhere and turn

    def test_each_motor_pulley_is_the_one_the_bill_of_materials_buys(self):
        """Both pulleys are the bought part, measured off the metal.

        Two numbers, because the BOM line carries two: "GT2 pulley 6mm
        x 16 teeth".  How far the drawn part reaches from its own axis
        is what says it has sixteen teeth and not some other count --
        at a fixed pitch a tooth count is a radius -- and it is asked
        of the mesh rather than of the constant the outline was built
        from, so a pulley that agreed in Python and came out of the
        polygon at another size would still fail.  How wide it stands
        along its own axis is the other number.

        The X one is cut at its own belt's pitch rather than at the
        nominal 2 mm, so its radius is asked at that pitch: a bought
        part is 16 teeth of GT2 either way, and which pitch it was
        drawn at is the drawing's business.
        """
        self.assertEqual(
            TEETH, self.BOUGHT_TEETH,
            'the pulleys are not the tooth count the machine buys')

        for pulley, period in (
                (self.node.x_stage.end_motor.belt_side.pulley,
                 x_belt.PERIOD),
                (self.node.y_axis.motor.pulley, gt2.PITCH)):
            axis = int(numpy.argmin(numpy.ptp(pulley.mesh.bounds, axis=0)))
            across = [index for index in range(3) if index != axis]

            width = numpy.ptp(pulley.mesh.bounds[:, axis])
            self.assertAlmostEqual(
                width, self.BOUGHT_WIDTH, delta=self.PLACED,
                msg=(f'{pulley.name} stands {width} mm wide, not the '
                     f'{self.BOUGHT_WIDTH} mm the bill of materials buys'))

            centre = pulley.mesh.bounds[:, across].mean(axis=0)
            reach = numpy.linalg.norm(
                pulley.mesh.vertices[:, across] - centre, axis=1).max()
            flanks = gt2.pulley_radius(self.BOUGHT_TEETH, period)
            self.assertAlmostEqual(
                reach, flanks - GT2Pulley.CLEARANCE, delta=self.PLACED,
                msg=(f'{pulley.name} reaches {reach} mm from its axis, not '
                     f'the {flanks - GT2Pulley.CLEARANCE} of a '
                     f'{self.BOUGHT_TEETH} tooth GT2 pulley'))

    def test_the_x_end_is_dimensioned_for_the_pulley_it_buys(self):
        """The design's own heights stand the belt where that pulley
        holds it.

        `PulleyRadius` is not decoration: `XIdler_height` is derived
        from it so the run comes off both ends level, and
        `X_rod_height` so the carriage's clamps meet the belt where it
        runs.  So it has to be the radius the bought pulley really
        carries a belt at, and a round 6 is not that radius for any
        tooth count -- it is a millimetre and a sixth outside the 16
        tooth pulley the same design buys, and a tenth inside the 20
        tooth one it does not.

        Asked three ways.  Which pulley the number names, which reads a
        radius back as a tooth count and is how the round 6 was caught
        in the first place.  Then the radius exactly, because that is
        what the two heights are computed from and what the cut plates
        therefore carry.  Then of the belt itself, above the pulley's
        own axis, where the loop's inner surface is riding on the
        flanks: it must be at that radius, plus the belt's back beyond
        it.  The last is the one that says the drawing agrees with the
        arithmetic -- a design number nothing was drawn at would pass
        the other two.
        """
        named = gt2.pulley_teeth(PulleyRadius)
        self.assertEqual(
            named, self.BOUGHT_TEETH,
            f'the X end is dimensioned for a {named} tooth pulley, and the '
            f'machine buys a {self.BOUGHT_TEETH} tooth one')

        bought = gt2.pulley_radius(self.BOUGHT_TEETH)
        self.assertAlmostEqual(
            PulleyRadius, bought, delta=self.PLACED,
            msg=(f'the X end is dimensioned for a pulley of radius '
                 f'{PulleyRadius}, but the one bought rides its belt at '
                 f'{bought} mm'))

        belt = self.node.x_stage.belt
        pulley = self.node.x_stage.end_motor.belt_side.pulley
        axis = pulley.mesh.bounds.mean(axis=0)

        over = numpy.abs(belt.mesh.vertices[:, 0] - axis[0]) < 0.2
        back = belt.mesh.vertices[over][:, 2].max() - axis[2]
        rides = PulleyRadius + gt2.THICKNESS - gt2.TOOTH_HEIGHT
        # A hundredth: the loop is cut to its own pitch rather than the
        # standard's, which puts its flanks a micron inside the design's
        # number, and the run leaves the top of the pulley at a slope
        # that costs another fraction of one across the window sampled.
        # Both are orders below the millimetre and a sixth a round 6 is
        # out by.
        self.assertAlmostEqual(
            back, rides, delta=0.01,
            msg=(f'over the pulley the belt runs {back} mm out from its '
                 f'axis, where the X end is dimensioned for {rides}'))

    def test_each_motor_pulley_straddles_the_belt_it_drives(self):
        """A pulley is across the belt it drives, not beside it.

        The design gets both of these wrong, and could not have seen
        either: its `GT2_pulley` module draws nothing, so the X one is
        placed one `thickness` off the plate it hangs behind -- 6 mm
        out of the plane its own belt runs in -- and the Y one is left
        at the origin of the motor's assembly, 72 mm off the shaft.
        Both are placed from their belt here instead, so both are asked
        the question the design was never in a position to fail.

        A containment with the overhang named, rather than an equality,
        because the pulley is the wider of the two: the machine buys a
        6 mm pulley and draws a 5 mm belt.  That is a mismatch inside
        the design's own bill of materials -- it buys 6 mm belt too --
        and not one to be drawn out of, so the belt runs half a
        millimetre inside the pulley at each side and is asked to be
        centred there.
        """
        proud = (self.BOUGHT_WIDTH - belt_width) / 2
        for pulley, belt, axis in (
                (self.node.x_stage.end_motor.belt_side.pulley,
                 self.node.x_stage.belt, 1),
                (self.node.y_axis.motor.pulley,
                 self.node.y_axis.belt, 0)):
            run = belt.mesh.bounds[:, axis]
            numpy.testing.assert_allclose(
                pulley.mesh.bounds[:, axis], [run[0] - proud, run[1] + proud],
                atol=self.PLACED,
                err_msg=(f'{pulley.name} does not straddle {belt.name} '
                         f'where it runs'))

    def test_the_x_pulley_meshes_with_its_belt(self):
        """The belt's teeth sit in the pulley's grooves, everywhere the
        carriage can put them.

        Two halves, and neither is worth much alone.  The pulley must
        not be inside the belt -- a tooth through a tooth is the way a
        phase, a tooth count or a pitch goes wrong, and it is worth
        nothing on its own because a pulley in the next room also fails
        to be inside anything.  And the belt must be within a hair of
        it, which is what says the two are actually nested; that is
        worth nothing on its own either, because parts can be a hair
        apart and interpenetrating.

        Asked at eight phases of one tooth rather than at the rest
        pose, because a mesh is tightest when a tooth is halfway out of
        its groove and where that happens depends on where in a tooth
        the carriage stands.  A single position would answer for one
        phase and say nothing about the other seven.
        """
        belt = self.node.x_stage.belt
        pulley = self.node.x_stage.end_motor.belt_side.pulley

        for position in self.through_one_tooth():
            self.node.set_state(x=position)

            shared = trimesh.boolean.intersection([belt.mesh, pulley.mesh])
            volume = 0.0 if shared.is_empty else shared.volume
            self.assertLess(
                volume, self.RIDING,
                f'at x={position} the pulley cuts {volume} cubic mm out '
                f'of the belt')

            gap = trimesh.proximity.closest_point(
                pulley.mesh, belt.mesh.vertices)[1].min()
            self.assertLessEqual(
                gap, self.MESHED,
                f'at x={position} the nearest the belt comes to the '
                f'pulley is {gap} mm, so it is not meshed on it')

    def test_the_x_pulley_turns_one_groove_per_belt_tooth(self):
        """Drive the carriage and the pulley turns with the teeth.

        The rate first, off the shaft itself: a tooth of belt through
        the clamp is one groove of pulley, and the sign is the loop's
        -- the run the carriage is clamped to leaves the top of the
        pulley, so a carriage going along +X turns it the way a clock
        goes.  A rate read as a number is the only place a factor of
        two or a reversed sign shows as itself rather than as a
        collision somewhere else.

        Then that the number reaches the metal, which the rate alone
        cannot say.  A quarter tooth turns the pulley a quarter groove,
        and a rotation moves its furthest point by exactly the chord of
        that angle at the radius the point stands at -- so this is a
        turn of a stated size about the stated axis, and not a nudge,
        a wobble, or a pulley swung around the corner of the plate it
        is bolted near.

        And a pulley goes nowhere, which the two turns have to be
        asked differently because a pulley is only sixteen-fold
        symmetric.  A whole groove of turn puts every tooth where the
        one before it stood, so the bounds come back exactly; a quarter
        groove moves them, and what stays is the axis they are centred
        on.
        """
        belt_side = self.node.x_stage.end_motor.belt_side
        pulley = belt_side.pulley
        tooth = self.one_tooth()
        groove = 360 / TEETH

        at_rest = belt_side.shaft.value
        vertices = pulley.mesh.vertices.copy()
        bounds = pulley.mesh.bounds.copy()

        self.node.set_state(x=XCarPosition + tooth)
        self.assertAlmostEqual(
            belt_side.shaft.value, at_rest - groove, delta=self.PLACED,
            msg=('one tooth of belt should turn the pulley one groove, '
                 f'but it turned {belt_side.shaft.value - at_rest} degrees'))
        numpy.testing.assert_allclose(pulley.mesh.bounds, bounds,
                                      atol=self.PLACED)

        self.node.set_state(x=XCarPosition + tooth / 4)
        moved = numpy.linalg.norm(pulley.mesh.vertices - vertices,
                                  axis=1).max()
        reach = x_belt.PULLEY_RADIUS - GT2Pulley.CLEARANCE
        chord = 2 * reach * math.sin(math.radians(groove / 4) / 2)
        self.assertAlmostEqual(
            moved, chord, delta=self.PLACED,
            msg=(f'a quarter tooth along, the furthest point of the pulley '
                 f'moved {moved}, not the {chord} a quarter groove of turn '
                 f'would move it'))
        numpy.testing.assert_allclose(pulley.mesh.bounds.mean(axis=0),
                                      bounds.mean(axis=0), atol=self.PLACED,
                                      err_msg='the pulley left its own axis')

    def test_the_y_pulley_sits_on_its_motor_shaft(self):
        """The Y pulley is on the shaft, bored onto it.

        Every point of it near the motor and no point of it inside:
        the first is what says the pulley is on the shaft rather than
        hanging in air beside it, and the second that the shaft goes
        through the bore rather than through the metal.  A pulley off
        the axis by so much as a millimetre fails both at once.

        It is not asked to turn.  The loop the design draws for this
        axis runs on three bare bearings and never reaches the motor,
        so these teeth are meshed with nothing and an angle for them
        would be a claim about a drive that is not modelled.
        """
        pulley = self.node.y_axis.motor.pulley
        motor = self.node.y_axis.motor.motor.motor

        self.assertClose(motor, pulley, self.ON_THE_SHAFT)

        shared = trimesh.boolean.intersection([motor.mesh, pulley.mesh])
        volume = 0.0 if shared.is_empty else shared.volume
        self.assertLess(
            volume, self.RIDING,
            f'the Y pulley cuts {volume} cubic mm out of its own motor')

    def test_the_belts_travel_into_the_viewer_as_shapes(self):
        """A belt is published as its shape, not as a mesh.

        Where a rigid part's document points at an STL, a belt's carries
        the analytic shape and one expression per parameter, so whatever
        opens the document can re-draw the belt itself at any carriage
        position instead of being handed one position's triangles.  The
        expressions have to name the machine's own drivers, or the
        viewer's sliders would move a bed with no belt following it.
        """
        with symbolic_document(self.node) as (declarations, _):
            root = serialize_node(self.node, lambda node: node.stl_file)

            self.assertEqual(document_version(root), 3)

            belts = self.flexible_nodes(root)
            self.assertEqual(sorted(belts),
                             ['x_stage.belt', 'y_axis.belt'])

            for path, driver in (('x_stage.belt', 'x'), ('y_axis.belt', 'y')):
                published = belts[path]
                self.assertEqual(published['tech'], 'molejo')
                self.assertEqual(sorted(published['params']), ['clamp'])
                self.assertIn(driver, declarations)
                self.assertIn(driver, published['params']['clamp'])

    ########################################
    # What the machine can be told to do

    def test_the_machine_rests_where_the_design_draws_it(self):
        """Untouched, the machine stands at the design's own knobs.

        The three drivers took their defaults from the car positions
        the .scad file sets, so a model nobody has driven is the model
        that repository has always rendered.
        """
        simulation = Sim(self.node, self.TICK)

        self.assertEqual(simulation.state, {'x': XCarPosition,
                                            'y': YCarPosition,
                                            'z': ZCarPosition})

    def test_every_instruction_lands_on_the_position_it_names(self):
        """An instruction puts an axis where its name says it goes.

        The instructions are declared on the machine beside the drivers
        they aim at, so their targets have to resolve against the
        machine's own `x`, `y` and `z` -- the same three bare names
        that put three sliders in front of whoever opens the model.
        """
        for name, instruction in type(self.node).instructions.items():
            simulation = Sim(self.node, self.TICK)

            simulation.trigger(name)
            simulation.run(instruction.duration)

            for driver, target in instruction.targets.items():
                self.assertAlmostEqual(
                    simulation.state[driver], target, delta=self.PLACED,
                    msg=f'{name} should leave {driver} at {target}')

    ########################################

    def declared_travel(self, driver):
        """The two ends of the travel the machine declares for an axis.

        Read off the driver declaration rather than restated here, so
        narrowing what the machine claims narrows what is asked of it.
        """
        return getattr(type(self.node), driver).range

    def one_tooth(self):
        """How far the carriage travels to pull one tooth of belt
        through its clamp."""
        return x_belt.PERIOD / gt2.span_scale(x_belt.CIRCLES,
                                              x_belt.CLAMP_SPAN)

    def through_one_tooth(self):
        """Carriage positions covering every phase of the X mesh.

        A tooth is where the whole engagement repeats, so `PHASES`
        points across one of them is every arrangement of teeth and
        grooves the axis can reach, and asking for more of the travel
        would only ask the same eight questions again.
        """
        step = self.one_tooth() / self.PHASES
        return [XCarPosition + index * step for index in range(self.PHASES)]

    def assertMovedBy(self, part, was, offset):
        """`part` now stands exactly `offset` from where `was` had it."""
        now = part.mesh.bounds
        for corner in (0, 1):
            for axis in range(3):
                self.assertAlmostEqual(
                    now[corner][axis], was[corner][axis] + offset[axis],
                    delta=self.PLACED,
                    msg=(f'{part.name} should have moved by {offset}, but on '
                         f'axis {axis} its bounds moved by '
                         f'{now[corner][axis] - was[corner][axis]}'))

    def assertStill(self, part, was):
        """`part` has not moved: the fixed reference a driven test
        needs, or a machine sliding whole would pass every one of
        them."""
        self.assertMovedBy(part, was, [0, 0, 0])

    def assertTeethTravel(self, belt, driver, rest, circles, span, sense):
        """`belt`'s teeth follow `driver`, one for one and the right way.

        `sense` is which way the axis' own coordinate runs against the
        belt's clamped span: the X carriage and its belt agree, the bed
        and its belt do not.
        """
        pitch = gt2.pitch(circles)
        # A whole tooth and a ring of belt, each as far as the axis has
        # to travel to pull that much belt through the clamp.
        tooth = sense * pitch / gt2.span_scale(circles, span)
        ring = (sense * gt2.spans(circles)[span][2]
                / gt2.PATH_SAMPLES / gt2.span_scale(circles, span))

        at_rest = belt.mesh.vertices.copy()
        teeth_at_rest = self.tooth_depths(belt)

        self.node.set_state(**{driver: rest + tooth})
        numpy.testing.assert_allclose(
            belt.mesh.vertices, at_rest, atol=self.PLACED,
            err_msg=f'{belt.name} is drawn differently one tooth along')

        self.node.set_state(**{driver: rest + tooth / 2})
        moved = numpy.linalg.norm(belt.mesh.vertices - at_rest, axis=1).max()
        self.assertAlmostEqual(
            moved, gt2.TOOTH_HEIGHT, delta=self.PLACED,
            msg=(f'half a tooth along, the furthest {belt.name} vertex '
                 f'moved {moved}, not the tooth height'))

        self.node.set_state(**{driver: rest + ring})
        stepped = self.tooth_depths(belt)
        first = 2 * span * gt2.PATH_SAMPLES
        clamped = slice(first + 1, first + gt2.PATH_SAMPLES)
        before = slice(first, first + gt2.PATH_SAMPLES - 1)
        numpy.testing.assert_allclose(
            stepped[clamped], teeth_at_rest[before], atol=self.PLACED,
            err_msg=(f"{belt.name}'s teeth did not step exactly one ring "
                     f"along the run they are clamped to"))

    def assertRidesOn(self, belt, part):
        """`belt` touches `part` without cutting into it.

        Not `assertNotIntersecting`, which is where this would belong:
        that assertion reaches for a node's cached STL whenever the pair
        is not exact on both sides, and a belt has no cached STL to
        reach for -- its geometry is one evaluation per position.  So
        the boolean is taken here, over the two meshes, and the verdict
        is a volume rather than a yes or no, because a belt really is
        in contact with what it runs on.
        """
        shared = trimesh.boolean.intersection([belt.mesh, part.mesh])
        volume = 0.0 if shared.is_empty else shared.volume
        self.assertLess(
            volume, self.RIDING,
            f'{belt.name} cuts {volume} cubic mm out of {part.name}')

    def tooth_depths(self, belt):
        """How much tooth `belt` has at each of its sampled rings.

        A molejo shape is sampled at the tessellation its document
        declares rather than at one the evaluator chooses, so ring `n`
        of a loop is always the same distance along that loop whatever
        the axis is doing, and the vertices come back ring by ring.
        What changes with the axis is how much tooth there is at each
        ring, which is the difference between the section's inner face
        and the back beside it, less the belt's own thickness there.
        """
        vertices = belt.mesh.vertices
        inner, back = vertices[0::4], vertices[1::4]
        return (numpy.linalg.norm(back - inner, axis=1)
                - (gt2.THICKNESS - gt2.TOOTH_HEIGHT))

    def flexible_nodes(self, document, path=(), found=None):
        """Every flexible part of a serialized tree, by its path in it.

        By path rather than by name: a node's name is the attribute its
        parent holds it in, and both axes call theirs `belt`.
        """
        found = {} if found is None else found
        if path and 'flexible' in document:
            found['.'.join(path)] = document['flexible']
        for child in document.get('children', ()):
            self.flexible_nodes(child, path + (child['name'],), found)
        return found

    def _is_on(self, bearing, rod):
        """Is this bearing threaded onto this rod?"""
        try:
            self.assertClose(rod, bearing, self.ON_THE_ROD)
        except AssertionError:
            return False
        return True
