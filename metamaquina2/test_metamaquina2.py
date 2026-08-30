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

The Z axis is asked something else again, because it is the one axis
whose driver is not a position.  A nut on a bar is a pair of parts that
must be inside each other's reach and out of each other's metal at the
same time, at every height and not only at the ones that happen to fall
on a whole pitch; and it must be a nut, which is to say it must not be
able to travel along the bar unless the bar turns.  Those are asked of
the exact solids rather than of two meshes, because that is what a
boundary kernel is for: the gap between a thread and its nut is a tenth
of a millimetre, and a tessellation is entitled to be wrong by that
much.

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

The springs are asked something else again, because half of what a
spring has to keep is not about the spring.  The catalogue line the
design buys them by gives a diameter and a free length and nothing
else, so the wire and the turn count are derived from what has to fit
-- inside the coil, and between one coil and the next -- and the tests
ask the metal for both rather than reading the derivation back.  The
length is asked of the gap: a spring has to touch what it stands on and
cut into nothing, and either half of that alone passes for something
wrong.  Where the design states a length for the same gap and the
statement disagrees with where its own parts stand, that disagreement
is asked for too, so it cannot quietly go away.

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

from metamaquina2 import gt2, jhead, thread, z_screw
from metamaquina2.hardware.gt2_pulley import TEETH, GT2Pulley
from metamaquina2.params import (
    BuildVolume_X,
    BuildVolume_Y,
    IdlerRadius,
    PTFE_liner_diameter,
    PTFE_liner_length,
    PulleyRadius,
    XCarPosition,
    XZStage_offset,
    YCarPosition,
    YPlatform_height,
    YPlatform_zoffset,
    ZCarPosition,
    belt_width,
    heatedbed_spring_compressed_length,
    jhead_instalation_depth,
    jhead_length,
    m3_washer_thickness,
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

    # How far from a pulley's axis a belt is still worth measuring
    # against it.
    #
    # `closest_point` compares every query point with every triangle at
    # once, so handing it a whole belt is gigabytes of intermediate --
    # and an out-of-memory kill on the Y loop, whose 32768 vertices
    # against 4224 pulley faces come to three -- for an answer that can
    # only come from the twenty millimetres of belt actually on the
    # pulley. Fifteen takes the wrapped arc and the tangent runs either
    # side of it; the nearest belt this excludes is the Y loop's bottom
    # run, 34 mm from that pulley's axis and in no danger of holding the
    # minimum.
    NEARBY = 15

    # An M8 nut is 14 mm across the flats on an 8 mm bar, so its
    # furthest corner is 8.1 mm off the axis and a bit over 4 mm out
    # from the crest of the thread it is threaded onto. Five separates
    # that from a nut hanging even a millimetre clear of its bar,
    # without depending on how a helix tessellates.
    ON_THE_BAR = 5

    # How far a Z nut may slide along its bar before the thread has to
    # stop it, and how far it may certainly not. The clearance the pair
    # is drawn with is a flank clearance, so the axial play it allows is
    # that much divided by the cosine of the flank angle -- 58 microns
    # here. Half of it must be free, because a fit that never touches
    # would pass the blocking half of this contract while being a hole;
    # twice it must foul, and by then the flanks are a good 30 microns
    # into each other, which no rounding reaches.
    Z_NUT_PLAY = thread.CLEARANCE / math.cos(math.radians(30)) / 2
    Z_NUT_STOP = thread.CLEARANCE / math.cos(math.radians(30)) * 2

    # A height in the middle of the Z travel that is deliberately NOT a
    # whole number of pitches up. A nut and a bar drawn with the wrong
    # sign on the turn, or with no turn at all, still line up wherever
    # the lift happens to be a whole number of leads -- the rest pose is
    # one such place and so is the bottom of the travel -- so the
    # question has to be asked somewhere between two threads.
    OFF_PITCH = 111.7

    # How far a spring may stand off the thing it is drawn to stand on.
    #
    # A coil touches a flat face along one tangent point, and what the
    # mesh puts there is the flat of a sixteen-sided section a
    # half-thousandth inside the wire's own circle. Five hundredths is
    # two orders above that and two orders below the three tenths of a
    # millimetre a spring drawn to the design's own compressed length
    # would float by, which is the mistake this separates.
    SEATED = 0.05

    # How near a spring's derived bore has to land on the clearance it
    # was derived for.
    #
    # Both surfaces are polygons inside their circles -- the shank a
    # sixty-gon, the wire's section a sixteen-gon -- so the measured
    # gap is a few thousandths wide of the exact one either way. Two
    # hundredths covers that and nothing else: a wire a tenth of a
    # millimetre out closes the bore by twice this.
    BORE = 0.02

    # Which element of the Y loop wraps which of its four circles. A
    # wrap runs span, arc, span, arc from the first circle, so the arc
    # about circle n is element 2n - 1, and `y_belt` lists them front,
    # lower, pulley, rear.
    LOWER_ARC = 1
    PULLEY_ARC = y_belt.PULLEY_ARC
    REAR_ARC = 5
    FRONT_ARC = 7

    def setUp(self):
        """Start every test from the rest pose.

        The runner rebinds the animation instant before each test but
        not the machine's own drivers, so a test that drives an axis
        would otherwise hand the next one a machine still driven.
        """
        self.drive(x=XCarPosition, y=YCarPosition, z=ZCarPosition)

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

        self.drive(z=ZCarPosition - 90)

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
            self.drive(z=height)
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

    def test_the_y_belt_rides_the_bar_idlers_on_its_smooth_back(self):
        """The three bearings carry the belt's back, not its teeth.

        Which is what "the teeth face outward" is, measured where it can
        be: a bare 608 race has nothing to mesh with, so a belt that
        presented its teeth to it would stand on their tips and its
        contact face would rise and fall a whole tooth height between
        one crest and the next.  This one is a smooth band, so every
        ring of every wrapped arc is at exactly the race's own radius.

        Asked of the arcs by name rather than of whatever happens to be
        near a bearing, because the straight runs leave on a tangent and
        the first millimetre of one is a hair off the race for reasons
        that have nothing to do with teeth.
        """
        bars = self.node.frame.bars
        belt = self.node.y_axis.belt
        for idler, element in ((bars.front.idler, self.FRONT_ARC),
                               (bars.rear.lower_idler, self.LOWER_ARC),
                               (bars.rear.upper_idler, self.REAR_ARC)):
            axis = idler.bearing.mesh.bounds.mean(axis=0)
            back = self.arc_rings(belt, element)[:, 0]
            reach = numpy.hypot(back[:, 1] - axis[1], back[:, 2] - axis[2])
            numpy.testing.assert_allclose(
                reach, IdlerRadius, atol=self.PLACED,
                err_msg=(f'the Y belt does not lie flat on '
                         f'{idler.bearing.name}'))

    def test_the_y_belt_turns_its_teeth_onto_the_pulley(self):
        """Over the pulley the belt is bent backwards, teeth inward.

        The other half of the same fact, and the half that makes the
        axis a drive.  Round the three bearings the loop is convex and
        the teeth stand outside it; round the pulley it is concave, the
        belt turns the other way, and the toothed face is the one
        against the metal.

        Measured as a range rather than a value, because that is what a
        tooth pattern is: on the pulley's arc the belt's toothed face
        reaches from the pulley's own flank circle, where the land
        between two teeth rides, to a whole tooth height inside it,
        where a crest sits in a groove.  A belt merely passing by would
        be a wrap's radius away from both.
        """
        pulley = self.node.y_axis.motor.pulley
        axis = pulley.mesh.bounds.mean(axis=0)
        toothed = self.arc_rings(self.node.y_axis.belt, self.PULLEY_ARC)[:, 1]
        reach = numpy.hypot(toothed[:, 1] - axis[1], toothed[:, 2] - axis[2])

        flanks = y_belt.PULLEY_RADIUS
        self.assertAlmostEqual(
            reach.max(), flanks, delta=self.PLACED,
            msg=(f'the land between the belt\'s teeth rides {reach.max()} mm '
                 f'from the pulley axis, not the {flanks} its flanks stand '
                 f'at'))
        self.assertAlmostEqual(
            reach.min(), flanks - gt2.TOOTH_HEIGHT, delta=self.PLACED,
            msg=(f'the belt\'s crests reach {reach.min()} mm from the pulley '
                 f'axis, not a tooth inside its flanks'))

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
                (self.node.y_axis.motor.pulley, y_belt.PERIOD)):
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

            gap = self.closest_to(pulley, belt)
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

        This is the contract that keeps the two placements honest.  The
        pulley is put where its belt is, in the belt's own frame, and
        the motor where the design's chain of mounting rotations puts
        it; nothing makes those agree except that the loop was drawn
        around the shaft the mount really carries.
        """
        pulley = self.node.y_axis.motor.pulley
        motor = self.node.y_axis.motor.motor.motor

        self.assertClose(motor, pulley, self.ON_THE_SHAFT)

        shared = trimesh.boolean.intersection([motor.mesh, pulley.mesh])
        volume = 0.0 if shared.is_empty else shared.volume
        self.assertLess(
            volume, self.RIDING,
            f'the Y pulley cuts {volume} cubic mm out of its own motor')

    def test_the_y_pulley_meshes_with_its_belt(self):
        """The belt's teeth sit in the Y pulley's grooves, everywhere
        the bed can put them.

        The same pair of halves the X pulley is held to, and for the
        same reasons -- a pulley in the next room also fails to be
        inside anything, and parts can be a hair apart and
        interpenetrating -- asked of a mesh the design never had.  Its
        own loop ran three bare bearings and stopped 22 mm short of
        this pulley; this one is bent backwards over it and wraps 156
        degrees of it.

        At eight phases of one tooth, because a mesh is tightest where
        a tooth is halfway out of its groove.
        """
        belt = self.node.y_axis.belt
        pulley = self.node.y_axis.motor.pulley

        for position in self.through_one_tooth(YCarPosition, y_belt, -1):
            self.node.set_state(y=position)

            shared = trimesh.boolean.intersection([belt.mesh, pulley.mesh])
            volume = 0.0 if shared.is_empty else shared.volume
            self.assertLess(
                volume, self.RIDING,
                f'at y={position} the pulley cuts {volume} cubic mm out '
                f'of the belt')

            gap = self.closest_to(pulley, belt)
            self.assertLessEqual(
                gap, self.MESHED,
                f'at y={position} the nearest the belt comes to the '
                f'pulley is {gap} mm, so it is not meshed on it')

    def test_the_y_pulley_turns_one_groove_per_belt_tooth(self):
        """Drive the bed and the pulley turns with the teeth.

        The rate first, off the shaft itself, and the sign is the
        reverse bend's: the belt turns counterclockwise about this
        pulley where it turns clockwise about every other circle in the
        loop, so a bed running towards the front of the machine turns
        it the way the X one is turned by a carriage running the other
        way.  A rate read as a number is the only place a factor of two
        or a reversed sign shows as itself rather than as a collision
        somewhere else.

        Then that the number reaches the metal, and that the pulley
        goes nowhere -- a whole groove of turn reproduces its bounds
        because it is sixteen-fold symmetric, a quarter groove moves
        them, and what survives both is the axis they are centred on.
        """
        motor = self.node.y_axis.motor
        pulley = motor.pulley
        tooth = self.one_tooth(y_belt, -1)
        groove = 360 / TEETH

        at_rest = motor.shaft.value
        vertices = pulley.mesh.vertices.copy()
        bounds = pulley.mesh.bounds.copy()

        self.node.set_state(y=YCarPosition + tooth)
        self.assertAlmostEqual(
            motor.shaft.value, at_rest + groove, delta=self.PLACED,
            msg=('one tooth of belt should turn the pulley one groove, '
                 f'but it turned {motor.shaft.value - at_rest} degrees'))
        numpy.testing.assert_allclose(pulley.mesh.bounds, bounds,
                                      atol=self.PLACED)

        self.node.set_state(y=YCarPosition + tooth / 4)
        moved = numpy.linalg.norm(pulley.mesh.vertices - vertices,
                                  axis=1).max()
        reach = y_belt.PULLEY_RADIUS - GT2Pulley.CLEARANCE
        chord = 2 * reach * math.sin(math.radians(groove / 4) / 2)
        self.assertAlmostEqual(
            moved, chord, delta=self.PLACED,
            msg=(f'a quarter tooth along, the furthest point of the Y pulley '
                 f'moved {moved}, not the {chord} a quarter groove of turn '
                 f'would move it'))
        numpy.testing.assert_allclose(pulley.mesh.bounds.mean(axis=0),
                                      bounds.mean(axis=0), atol=self.PLACED,
                                      err_msg='the pulley left its own axis')

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

            # By the parameter rather than by counting what is
            # flexible: the springs are flexible leaves too, and this
            # contract is the belts'.
            belts = {path: published
                     for path, published in self.flexible_nodes(root).items()
                     if sorted(published['params']) == ['clamp']}
            self.assertEqual(sorted(belts),
                             ['x_stage.belt', 'y_axis.belt'])

            for path, driver in (('x_stage.belt', 'x'), ('y_axis.belt', 'y')):
                published = belts[path]
                self.assertEqual(published['tech'], 'molejo')
                self.assertEqual(sorted(published['params']), ['clamp'])
                self.assertIn(driver, declarations)
                self.assertIn(driver, published['params']['clamp'])

    ########################################
    # The springs, which are as long as the space they are left

    def test_the_machine_carries_six_springs_as_flexible_leaves(self):
        """Four under the bed and two on the extruder handle.

        A spring's shape follows the machine the way a belt's does --
        squeeze it and it is a different solid, not the same solid
        somewhere else -- so it makes no time-invariance promise and
        the tree has to know that about it.  One port each, and it is
        the length: everything else about a spring is the part that was
        bought.
        """
        springs = [spring for spring, _ in self.springs()]
        self.assertEqual(len(springs), 6)

        for spring in springs:
            self.assertTrue(spring.flexible, f'{spring.name} is not flexible')
            self.assertFalse(spring.rigid,
                             f'{spring.name} claims to be rigid')
            self.assertEqual(spring.tech, 'molejo')
            self.assertEqual(sorted(spring.bound_values()), ['height'])

    def test_each_spring_is_one_closed_coil(self):
        """A spring is a single closed band of wire.

        Swept from a closed section along a helix, so it is watertight
        by construction rather than by repair.  What this catches is
        the construction going wrong: a coil left open at an end, or a
        section wound the wrong way round.
        """
        for spring, _ in self.springs():
            mesh = spring.mesh
            self.assertTrue(mesh.is_watertight,
                            f'{spring.name} is not a closed coil')
            self.assertEqual(len(mesh.split(only_watertight=False)), 1,
                             f'{spring.name} came out in pieces')
            self.assertGreater(mesh.volume, 0,
                               f'{spring.name} is inside out')

    def test_each_bed_spring_stands_between_the_platform_and_the_bed(self):
        """A bed spring fills the gap and neither floats nor bites.

        The two halves have to be asked together.  A spring drawn to
        the design's own `heatedbed_spring_compressed_length` would
        clear the platform it stands on by three tenths of a
        millimetre and still pass any check that only asked it not to
        interfere; one drawn a little long would pass any check that
        only asked it to touch.
        """
        platform = self.node.y_axis.platform
        for screw in platform.level_screws:
            self.assertSeatedOn(screw.spring, platform.plate)
            self.assertSeatedOn(screw.spring, screw.seat_washer)

    def test_the_bed_springs_follow_the_gap_and_not_the_design_number(self):
        """The spring is as long as its neighbours leave it, and the
        design's own number for that length is out.

        `pcb_height` counts `heatedbed_spring_compressed_length` up
        from a deck at `YPlatform_height`, while
        `YPlatform_subassembly` stands that deck at a literal `100-15`.
        The two differ, so the design states this one gap twice and
        disagrees with itself; the spring follows the parts.
        """
        platform = self.node.y_axis.platform
        screw = platform.level_screws[0]

        gap = (platform.heated_bed.pcb.mesh.bounds[0][2]
               - platform.plate.mesh.bounds[1][2])

        self.assertAlmostEqual(
            screw.spring.installed + m3_washer_thickness, gap,
            delta=self.PLACED,
            msg='the spring and its washer do not fill the gap they are in')
        self.assertAlmostEqual(
            heatedbed_spring_compressed_length - gap,
            YPlatform_zoffset - YPlatform_height, delta=self.PLACED,
            msg=("the design's spring length and the gap its own parts "
                 "leave no longer differ by its two statements of the deck"))

    def test_the_bed_springs_travel_with_the_bed(self):
        """Driving Y carries the springs, because they are the bed's.

        A spring is redrawn at every render, so a placement mistake
        here would not show as a part left behind: it would show as a
        spring drawn correctly in the wrong place, which is why this
        asks the bounds rather than the shape.
        """
        platform = self.node.y_axis.platform
        at_rest = [screw.spring.mesh.bounds
                   for screw in platform.level_screws]

        self.drive(y=YCarPosition - 70)

        for screw, was in zip(platform.level_screws, at_rest):
            self.assertMovedBy(screw.spring, was, [0, -70, 0])

    def test_each_idler_spring_seats_on_the_idler_back_plate(self):
        """The idler springs push the arm shut, not open.

        Which side of the back plate a spring stands on is the whole
        question: on the far side it presses the bearing onto the
        filament, on the near side it would pull the idler away from
        the hobbed bolt and the extruder would grip nothing.
        """
        extruder = self.node.x_stage.carriage.extruder
        plate = extruder.idler.back_plate

        # Which side is which, without naming an axis: the lever is at
        # one end of the bolts and the head at the other, so the spring
        # is on the right side of the plate when it stands further from
        # the lever than the plate does.
        lever = extruder.handle.plate.mesh.bounds.mean(axis=0)
        beyond = numpy.linalg.norm(
            plate.mesh.bounds.mean(axis=0) - lever)

        for spring, washer in zip(extruder.handle.springs,
                                  extruder.handle.spring_washers):
            self.assertSeatedOn(spring, washer)
            self.assertSeatedOn(washer, plate)
            self.assertGreater(
                numpy.linalg.norm(spring.mesh.bounds.mean(axis=0) - lever),
                beyond,
                f'{spring.name} stands on the lever side of {plate.name}, '
                f'where compressing it would swing the idler open')

    def test_each_spring_clears_the_bolt_it_is_threaded_on(self):
        """A spring runs on its bolt without touching it.

        The bill of materials names a spring by an outside diameter
        only, so the wire is derived from what has to fit inside it:
        this is that derivation asked of the metal.  A wire drawn too
        thick closes the bore onto the shank; too thin and the spring
        is a different spring from the one that was bought.
        """
        for spring, bolt in self.springs():
            gap = trimesh.proximity.closest_point(
                bolt.mesh, spring.mesh.vertices)[1].min()
            self.assertAlmostEqual(
                gap, spring.bore_clearance / 2, delta=self.BORE,
                msg=(f'{spring.name} runs {gap} mm off {bolt.name}, not the '
                     f'{spring.bore_clearance / 2} its bore is derived for'))

    def test_each_spring_stands_open_at_the_length_it_is_installed(self):
        """The coils clear each other, and the spring is compressed.

        The catalogue line gives a diameter and a free length and no
        coil count, so the count is derived from the room there is for
        one: the most whole turns that still leave a wire's thickness
        between consecutive coils where the design installs the spring.

        No spring is drawn longer than it is free, because a stretched
        compression spring is not a drawing of anything.  The bed's
        four are drawn shorter, because the gap the design leaves them
        is shorter than they are; the extruder's two are drawn at free
        length, because the design draws their tension nut at the very
        end of its thread and names no setting in from there.
        """
        platform = self.node.y_axis.platform

        for spring, _ in self.springs():
            clearance = spring.height.value / spring.turns
            self.assertGreaterEqual(
                clearance, 2 * spring.wire_diameter,
                f'{spring.name} closes on itself at the length it is in')
            self.assertLessEqual(
                spring.installed, spring.free_length,
                f'{spring.name} is drawn longer than its free length')

        for screw in platform.level_screws:
            self.assertLess(
                screw.spring.installed, screw.spring.free_length,
                f'{screw.spring.name} carries no load under the bed')

    def test_the_springs_travel_into_the_viewer_as_shapes(self):
        """A spring is published as its shape, not as a mesh.

        The same contract the belts keep, and for the day the bed's
        level or the idler's release becomes a driver: whatever opens
        the document has to be able to redraw a spring at a length
        nobody has evaluated yet.
        """
        with symbolic_document(self.node) as (_, __):
            root = serialize_node(self.node, lambda node: node.stl_file)

            flexible = self.flexible_nodes(root)
            springs = {path: published
                       for path, published in flexible.items()
                       if sorted(published['params']) == ['height']}

            self.assertEqual(len(springs), 6)
            for path, published in springs.items():
                self.assertEqual(published['tech'], 'molejo', path)
                self.assertEqual(published['spec']['path'][0]['type'],
                                 'helix', path)

    ########################################
    # The hot end, which is where Z is measured from

    def test_the_extruder_carries_the_hot_end_it_buys(self):
        """The five bought parts are there, and the two bolts that hold
        them.

        Five parts and not one solid, because that is what a builder
        has in front of them: a PEEK holder, a PTFE liner to push down
        it, a brass nozzle to screw into its foot, and a resistor and a
        thermistor to push into the brass.  The bill of materials buys
        each of them separately, three under `//TODO: Add this part to
        the CAD model`.
        """
        hot_end = self.node.x_stage.carriage.extruder.hot_end

        for part in ('holder', 'liner', 'nozzle', 'resistor', 'thermistor'):
            self.assertTrue(hasattr(hot_end, part),
                            f'the hot end has no {part}')
            self.assertGreater(getattr(hot_end, part).mesh.volume, 0,
                               f"the hot end's {part} is empty")

        bolts = self.node.x_stage.carriage.extruder.hot_end_bolts
        self.assertEqual(len(bolts), 2)

    def test_the_nozzle_tip_stands_where_the_machine_measures_z_from(self):
        """The tip is `jhead_length` less its installation depth below
        the face the extruder clamps.

        This is the contract the whole hot end exists to keep, and the
        one that decides the holder's length.  `nozzle_tip_distance`
        lifts the entire X platform by exactly this much so that the tip
        stands `ZCarPosition` above the build surface; a hot end drawn
        at either of the lengths its own drawing offers would put the
        tip somewhere else and leave the machine measuring from a point
        no part reaches.

        Asked in three places at once, because each alone passes for
        something wrong: the holder has to stand its shoulder on the
        extruder's underside, the collar and neck above that have to be
        the depth the design says they are, and the brass has to reach
        down from there to the tip.
        """
        extruder = self.node.x_stage.carriage.extruder
        hot_end = extruder.hot_end

        mount = hot_end.holder.mesh.bounds[1][2] - jhead.INSTALLATION
        underside = min(sheet.mesh.bounds[0][2]
                        for sheet in extruder.block.slices)

        self.assertAlmostEqual(
            jhead.INSTALLATION, jhead_instalation_depth, delta=self.PLACED,
            msg=("the holder's collar and neck are not the design's own "
                 "installation depth"))
        self.assertAlmostEqual(
            mount, underside, delta=self.PLACED,
            msg="the holder's shoulder is not on the extruder's underside")
        self.assertAlmostEqual(
            mount - hot_end.nozzle.mesh.bounds[0][2],
            jhead_length - jhead_instalation_depth, delta=self.PLACED,
            msg='the nozzle tip is not where the machine measures Z from')

    def test_homing_z_brings_the_nozzle_down_onto_the_build_surface(self):
        """`HomeZ` really does put the nozzle on the glass.

        What the beam does at the bottom of the travel was already
        asked; what it is *for* could not be, because there was no
        nozzle to ask about.  Both halves again: a tip that stops short
        has not homed, and a tip through the glass has homed to the
        wrong place.
        """
        nozzle = self.node.x_stage.carriage.extruder.hot_end.nozzle
        glass = self.node.y_axis.platform.heated_bed.glass

        simulation = Sim(self.node, self.TICK)
        simulation.trigger('HomeZ')
        simulation.run(z_screw.HOMING_TIME)

        self.assertAlmostEqual(
            nozzle.mesh.bounds[0][2], glass.mesh.bounds[1][2],
            delta=self.PLACED,
            msg='the homed nozzle does not meet the build surface')

    def test_the_hot_end_is_stacked_the_way_it_is_assembled(self):
        """Each part of the hot end stands on the next one.

        The nozzle is run into the holder's foot until its block meets
        the shoulder; the liner is pushed down the bore until its point
        comes to rest on the rim of the melt chamber.  Both are contact,
        so both are asked as contact: touching, and cutting into
        nothing.

        The two are not asked the same way round, because they are not
        the same kind of contact.  The nozzle meets the holder face to
        face, so either part's vertices land on the other.  The liner
        does not meet a face at all -- a cone comes down on a circle --
        and a cone drawn with a ring at each end has no vertex where it
        touches, while the rim has one all the way round.  So the rim is
        what is asked.
        """
        hot_end = self.node.x_stage.carriage.extruder.hot_end

        self.assertSeatedOn(hot_end.nozzle, hot_end.holder)

        self.assertRidesOn(hot_end.liner, hot_end.nozzle)
        rim = trimesh.proximity.closest_point(
            hot_end.liner.mesh, hot_end.nozzle.mesh.vertices)[1].min()
        self.assertLess(
            rim, self.SEATED,
            f'the liner stands {rim} mm clear of the melt chamber rim')

    def test_no_two_parts_of_the_hot_end_share_metal(self):
        """Five parts that fit inside each other, and none of them in
        each other.

        The one place in this machine where that can be asked of every
        pair -- the design's fasteners pass through the sheets they
        clamp and its bought parts come in several bodies, which is why
        the whole-model contract is not asserted, but a hot end really
        is five separate things.
        """
        hot_end = self.node.x_stage.carriage.extruder.hot_end
        parts = [hot_end.holder, hot_end.liner, hot_end.nozzle,
                 hot_end.resistor, hot_end.thermistor]

        for first in range(len(parts)):
            for second in range(first + 1, len(parts)):
                self.assertRidesOn(parts[first], parts[second])

    def test_the_liner_runs_the_bore_it_was_derived_for(self):
        """The liner fills the holder's bore at the derived clearance.

        The bore was not measured off anything: it is the groove root
        the design draws its own body around, less the thinnest wall its
        drawing leaves at a groove, and what makes that derivation worth
        anything is that the liner the design draws goes down it.  So
        the metal is asked, rather than the arithmetic read back.
        """
        hot_end = self.node.x_stage.carriage.extruder.hot_end
        clearance = (jhead.bore - PTFE_liner_diameter) / 2

        gap = trimesh.proximity.closest_point(
            hot_end.holder.mesh, hot_end.liner.mesh.vertices)[1].min()
        self.assertAlmostEqual(
            gap, clearance, delta=self.BORE,
            msg=f'the liner runs {gap} mm off the bore, not {clearance}')

    def test_the_liner_is_drawn_to_the_room_the_hot_end_leaves_it(self):
        """The liner is shorter than its own drawing by the room that
        is missing.

        `PTFE_liner.scad` draws 47 mm and the hot end has 40.3 mm of
        bore to offer, and the difference is not a rounding: it is more
        than six millimetres of tube with nowhere to be.  Asked so that
        the disagreement cannot quietly go away -- if the design's liner
        and the design's overall length are ever reconciled, this is
        what says so.
        """
        liner = self.node.x_stage.carriage.extruder.hot_end.liner
        low, high = liner.mesh.bounds

        self.assertAlmostEqual(
            high[2] - low[2], PTFE_liner_length - jhead.LINER_SHORTFALL,
            delta=self.PLACED)
        self.assertGreater(jhead.LINER_SHORTFALL, 1)

    def test_the_heater_and_the_sensor_sit_in_their_drilled_holes(self):
        """Both are in the holes the nozzle module drills for them.

        Each one is asked the same two questions a part pressed into a
        hole has to answer: it stays inside the hole, and it comes out
        of it far enough to be wired.  Inside rather than on the axis,
        because a drilled hole is round and a part in it is a polygon:
        asking every point of the part to be within the hole's own
        radius of its axis is the same contract without a tessellation
        in it, and it is the one that would catch a resistor pushed into
        the wrong hole or drawn oversize.

        That the part is not in the brass is the pairwise contract next
        door, and it is what the slip fit is drawn for -- a body at
        exactly the drilled diameter would be the same circle twice, and
        the pair could not be asked at all.
        """
        hot_end = self.node.x_stage.carriage.extruder.hot_end
        block = hot_end.nozzle.mesh.bounds

        # Where the filament axis stands, read off the block itself
        # rather than off the carriage: the block's own corner is what
        # both holes are dimensioned from, and it is the same corner
        # wherever the machine has sent the carriage.  The design draws
        # the hot end square with the machine, so the block's X is the
        # machine's.
        axis_x = block[0][0] + jhead.BLOCK_BORE_X
        axis_y = block[0][1] + jhead.BLOCK_BORE_Y
        base = block[0][2] + jhead.REACH

        for part, along, hole, drilled in (
                (hot_end.resistor, 1,
                 (axis_x + jhead.HEATER_X, base + jhead.HEATER_HEIGHT),
                 jhead.HEATER_DIAMETER),
                (hot_end.thermistor, 0,
                 (axis_y + jhead.THERMISTOR_Y,
                  base + jhead.THERMISTOR_HEIGHT),
                 jhead.THERMISTOR_DIAMETER)):
            across = [index for index in range(3) if index != along]
            offsets = part.mesh.vertices[:, across] - numpy.array(hole)
            radius = numpy.linalg.norm(offsets, axis=1).max()

            self.assertLessEqual(
                radius, drilled / 2,
                f'{part.name} stands outside the hole drilled for it')
            self.assertLess(
                part.mesh.bounds[0][along], block[0][along],
                f'{part.name} does not reach out of the block to be wired')

    def test_the_hot_end_travels_with_the_carriage_and_the_beam(self):
        """The nozzle goes where the machine sends it.

        Driving X slides it along the beam and driving Z takes it down
        with the beam, which is the whole reason the tip is worth
        measuring: a hot end bolted to the frame by accident would keep
        every other contract here.
        """
        nozzle = self.node.x_stage.carriage.extruder.hot_end.nozzle

        at_rest = nozzle.mesh.bounds.copy()
        self.drive(x=XCarPosition + 40)
        self.assertMovedBy(nozzle, at_rest, [40, 0, 0])

        self.drive(x=XCarPosition)
        at_rest = nozzle.mesh.bounds.copy()
        self.drive(z=ZCarPosition - 30)
        self.assertMovedBy(nozzle, at_rest, [0, 0, -30])

    ########################################
    # What the machine can be told to do

    def test_the_machine_rests_where_the_design_draws_it(self):
        """Untouched, the machine stands at the design's own knobs.

        The three drivers took their defaults from the car positions
        the .scad file sets, so a model nobody has driven is the model
        that repository has always rendered.  Z says it in degrees of
        screw, because that is what Z's state is, and the height those
        degrees are worth is the one the .scad file draws.
        """
        simulation = Sim(self.node, self.TICK)

        self.assertEqual(simulation.state,
                         {'x': XCarPosition,
                          'y': YCarPosition,
                          'z': z_screw.angle(ZCarPosition)})
        self.assertAlmostEqual(z_screw.lift(simulation.state['z']),
                               ZCarPosition, delta=self.PLACED)

    def test_every_instruction_lands_on_the_position_it_names(self):
        """An instruction puts an axis where its name says it goes.

        The instructions are declared on the machine beside the drivers
        they aim at, so their targets have to resolve against the
        machine's own `x`, `y` and `z` -- the same three bare names
        that put three sliders in front of whoever opens the model.

        A target is in millimetres and a driver's state need not be, so
        the two are compared through the declaration that knows the
        difference.  That is the whole of what `scale` buys: an
        instruction says where to go and stays out of the machinery.
        """
        for name, instruction in type(self.node).instructions.items():
            simulation = Sim(self.node, self.TICK)

            simulation.trigger(name)
            simulation.run(instruction.duration)

            for driver, target in instruction.targets.items():
                native = getattr(type(self.node), driver).native(target)
                self.assertAlmostEqual(
                    simulation.state[driver], native, delta=self.PLACED,
                    msg=f'{name} should leave {driver} at {target}')

    def test_homing_z_winds_the_beam_down_to_the_build_surface(self):
        """`HomeZ` goes to the bottom, and takes a screw's time to.

        Home on this axis is nought -- the endstop is under the beam,
        not over it -- so this asks for the bottom of the travel and
        not the top, and asks the beam rather than the driver: the
        nozzle really has to arrive at the build surface.

        The rate is the other half, and the half a fast animation would
        get wrong.  From the rest pose the instruction has the whole
        declared travel to cover in `z_screw.HOMING_TIME`, which is
        that travel at Marlin's own Z homing feedrate, so a third of
        the way through the run the beam is a third of the way down and
        not somewhere a belt would have got to.
        """
        beam = self.node.x_stage.plate
        at_rest = beam.mesh.bounds.copy()
        part = z_screw.HOMING_TIME / 3

        simulation = Sim(self.node, self.TICK)
        simulation.trigger('HomeZ')
        simulation.run(part)

        self.assertAlmostEqual(
            z_screw.lift(simulation.state['z']),
            ZCarPosition - part * z_screw.HOMING_RATE, delta=self.PLACED,
            msg='homing Z does not descend at the rate the screws turn')

        simulation.run(z_screw.HOMING_TIME - part)

        self.assertAlmostEqual(z_screw.lift(simulation.state['z']), 0.0,
                               delta=self.PLACED)
        self.assertMovedBy(beam, at_rest, [0, 0, -ZCarPosition])

    ########################################
    # The Z screws, which lift by turning

    def test_each_z_nut_is_threaded_onto_its_bar(self):
        """Both nuts are on a bar, and neither is in one.

        Two halves that are worth nothing apart, which is why they are
        one test.  A nut that shares no metal with its bar has cleared
        it -- and so has a nut in the next room.  A nut whose every
        point is within a few millimetres of the bar is on the axis --
        and so is a nut machined straight through the thread.  Together
        they are the only thing "threaded onto" can mean to two solids.
        """
        for nut, bar in self.z_pairs():
            self.assertNotIntersecting(bar, nut)
            self.assertClose(bar, nut, self.ON_THE_BAR)

    def test_the_nuts_stay_threaded_wherever_the_screws_are_turned(self):
        """The pair keeps clear at heights that are not whole threads.

        This is the contract the rest pose cannot state.  A nut and a
        bar that are drawn without any turn at all, or with the turn
        the wrong way round, still fall neatly into each other wherever
        the lift happens to be a whole number of leads -- and the rest
        pose is 120 leads up, and the bottom of the travel is nought.
        So it is asked at the bottom, where a homed machine sits, and
        once in the middle at a height deliberately between two
        threads, which is where a bar that was not really turning
        drives its crest through the nut's.
        """
        for height in (0.0, self.OFF_PITCH):
            self.drive(z=height)
            for nut, bar in self.z_pairs():
                self.assertNotIntersecting(bar, nut)

    def test_the_bars_sustain_the_nuts(self):
        """A nut cannot travel its bar unless the bar turns.

        Which is what holds the X stage up: the beam's weight is on two
        nuts, and what stops them running down the bars is that a
        thread is in the way.  Pushed along the axis by a fraction of a
        millimetre the nut fouls the flank it is resting on, and that
        is a load path rather than a coincidence of placement -- the
        same push on a nut around a plain cylinder meets nothing at
        all, which is exactly what this machine used to be.

        Asked both ways, because a screw drive holds a beam up and also
        stops it being pushed up, and asked with its play named: a fit
        that never touches would pass the blocking half of this on a
        bore of any size, so the nut has to be genuinely free inside
        its backlash and genuinely stopped outside it.
        """
        for nut, bar in self.z_pairs():
            self.assertFreeWithin(nut, self.Z_NUT_PLAY, bar, along=(0, 0, 1))
            self.assertBlockedBeyond(nut, self.Z_NUT_STOP, bar,
                                     along=(0, 0, 1))

    def test_a_whole_turn_of_the_bars_lifts_the_beam_one_lead(self):
        """One turn, one pitch, and the bars go nowhere doing it.

        A bar is not symmetric about its own axis in any way but one: a
        whole turn puts every thread where the one before it stood, so
        a bar drawn a lead further down its travel comes back drawn
        exactly as it was.  That is the rate read off the metal rather
        than off the arithmetic -- a bar geared to half or twice the
        lead would come back somewhere else -- and the beam has to have
        moved that lead while it happened, or the two are not the same
        drive.
        """
        beam = self.node.x_stage.plate
        beam_at_rest = beam.mesh.bounds.copy()
        bars_at_rest = [bar.mesh.vertices.copy()
                        for bar in self.node.z_axis.bars.bars]

        self.drive(z=ZCarPosition - z_screw.LEAD)

        for bar, at_rest in zip(self.node.z_axis.bars.bars, bars_at_rest):
            numpy.testing.assert_allclose(
                bar.mesh.vertices, at_rest, atol=self.PLACED,
                err_msg=(f'{bar.name} is drawn differently a whole turn '
                         f'along'))
        self.assertMovedBy(beam, beam_at_rest, [0, 0, -z_screw.LEAD])

    def test_lifting_the_beam_turns_both_bars_the_way_a_screw_turns(self):
        """A quarter lead of rise is a quarter turn, clockwise.

        The sign is the whole point and it is the thread's, not a
        convention: an M8 bar is right-handed, so the turn that drives
        a captive nut UP the bar is the one that would loosen a bolt
        seen from below and tighten it seen from above -- clockwise
        from above, which is negative about Z.  Read as an angle off
        the metal, which is the only place a reversed drive shows as
        itself instead of as a collision two tests later.

        Both bars, and by the same angle: they turn together or the
        beam racks.
        """
        quarter = -360 / 4

        for bar in self.node.z_axis.bars.bars:
            turned = self.turned_lifting(bar, z_screw.LEAD / 4)
            self.assertAlmostEqual(
                turned, quarter, delta=self.PLACED,
                msg=(f'a quarter lead of rise turned {bar.name} {turned} '
                     f'degrees, not the {quarter} of a quarter turn'))

    def test_the_couplings_turn_with_the_bars_they_clamp(self):
        """A coupling goes round with its shaft, or it is a sleeve.

        Clamped to the motor shaft at one end and to the bar at the
        other, so there is no ratio to state and nothing to check but
        that it is the same angle: a coupling standing still under a
        turning bar would be the model saying the bolts are loose.
        """
        for coupling in self.node.z_axis.couplings.couplings:
            turned = self.turned_lifting(coupling, z_screw.LEAD / 4)
            self.assertAlmostEqual(
                turned, -360 / 4, delta=self.PLACED,
                msg=f'{coupling.name} does not turn with its bar')

    ########################################

    def drive(self, **positions):
        """Send the machine to positions stated in millimetres.

        A driver's state is not always a position: Z's is the angle its
        screws stand at, and millimetres reach it through the `scale`
        the declaration carries.  Every test says where it wants the
        machine in the units a maker would, and the declaration
        converts -- which is the same route an instruction target
        takes, so a test cannot be right about a height the interface
        would be wrong about.
        """
        self.node.set_state(**{
            name: getattr(type(self.node), name).native(value)
            for name, value in positions.items()})

    def declared_travel(self, driver):
        """The two ends of the travel the machine declares for an axis.

        Read off the driver declaration rather than restated here, so
        narrowing what the machine claims narrows what is asked of it.
        """
        return getattr(type(self.node), driver).range

    def z_pairs(self):
        """Each Z nut with the bar it is threaded onto.

        Paired by side rather than by name: `ZBars` lists its bars from
        the left of the machine, and the X ends are held one each on
        the beam, so the motor end's nut belongs to the first bar.
        """
        return list(zip((self.node.x_stage.end_motor.nut,
                         self.node.x_stage.end_idler.nut),
                        self.node.z_axis.bars.bars))

    def z_axes(self):
        """Where the two Z bars stand, in the machine's own XY."""
        offset = self.node.z_axis.bars.offset
        return [numpy.array([side * offset, -XZStage_offset])
                for side in (-1, 1)]

    def turned_lifting(self, part, rise):
        """How far `part` turns about its own Z bar's axis when the beam
        is lifted `rise` millimetres from the bottom of its travel.

        Signed, and about the axis the part really stands on rather
        than about the middle of the machine: a rotation and a swing
        both move a part, and only one of them is a screw turning.  The
        angle is read off the vertex furthest from that axis, where a
        turn shows largest and a float shows least.
        """
        axis = min(self.z_axes(),
                   key=lambda candidate: numpy.linalg.norm(
                       part.mesh.bounds.mean(axis=0)[:2] - candidate))

        self.drive(z=0.0)
        before = part.mesh.vertices[:, :2].copy() - axis
        self.drive(z=rise)
        after = part.mesh.vertices[:, :2] - axis

        furthest = int(numpy.hypot(*before.T).argmax())
        start, end = before[furthest], after[furthest]
        return math.degrees(math.atan2(start[0] * end[1] - start[1] * end[0],
                                       start @ end))

    def one_tooth(self, belt=x_belt, sense=1):
        """How far an axis travels to pull one tooth of belt through its
        clamp.

        `sense` is which way the axis' own coordinate runs against the
        belt's clamped span, as `assertTeethTravel` means it: the X
        carriage and its belt agree, the bed and its belt do not.
        """
        return sense * belt.PERIOD / gt2.span_scale(belt.CIRCLES,
                                                    belt.CLAMP_SPAN)

    def through_one_tooth(self, rest=XCarPosition, belt=x_belt, sense=1):
        """Axis positions covering every phase of a mesh.

        A tooth is where the whole engagement repeats, so `PHASES`
        points across one of them is every arrangement of teeth and
        grooves the axis can reach, and asking for more of the travel
        would only ask the same eight questions again.
        """
        step = self.one_tooth(belt, sense) / self.PHASES
        return [rest + index * step for index in range(self.PHASES)]

    def closest_to(self, part, belt):
        """How near `belt` comes to `part`, over the belt around it.

        A minimum over a neighbourhood rather than over the whole loop,
        for the reason `NEARBY` gives; the rest of the belt is hundreds
        of millimetres away and cannot hold the answer.
        """
        axis = part.mesh.bounds.mean(axis=0)
        vertices = belt.mesh.vertices
        near = vertices[
            numpy.linalg.norm(vertices - axis, axis=1) < self.NEARBY]
        self.assertGreater(
            len(near), 0,
            f'no part of {belt.name} comes within {self.NEARBY} mm of '
            f'{part.name}')
        return trimesh.proximity.closest_point(part.mesh, near)[1].min()

    def arc_rings(self, belt, element):
        """The sampled rings of one element of a loop, as (N, 4, 3).

        A molejo shape is sampled at the tessellation its document
        declares, and a wrap spends `PATH_SAMPLES` rings on each of its
        two-per-circle elements in order, so which rings belong to which
        arc is a fact about the document rather than a search through
        the mesh.  The four vertices of a ring are the section's own
        four points in order, so column 0 is the loop's inner face and
        column 1 its outer.
        """
        rings = belt.mesh.vertices.reshape(-1, 4, 3)
        return rings[element * gt2.PATH_SAMPLES:
                     (element + 1) * gt2.PATH_SAMPLES]

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

    def springs(self):
        """Every spring in the machine, with the bolt it runs on.

        Paired rather than listed, because half of what a spring has to
        keep is a relationship to the shank inside it: the wire's
        thickness is derived from the room there is between the two.
        """
        platform = self.node.y_axis.platform
        handle = self.node.x_stage.carriage.extruder.handle
        return ([(screw.spring, screw.bolt)
                 for screw in platform.level_screws]
                + list(zip(handle.springs, handle.bolts)))

    def assertSeatedOn(self, spring, part):
        """`spring` stands on `part`: touching it, and cutting into
        nothing.

        Both halves, because either alone passes for something wrong --
        a spring floating in its gap keeps the first, a spring drawn
        through the sheet under it keeps the second. The boolean is
        taken here rather than through `assertNotIntersecting` for the
        reason `assertRidesOn` gives: a flexible part has no cached STL
        for that assertion to reach for.
        """
        self.assertRidesOn(spring, part)
        reach = trimesh.proximity.closest_point(
            part.mesh, spring.mesh.vertices)[1].min()
        self.assertLess(
            reach, self.SEATED,
            f'{spring.name} stands {reach} mm clear of {part.name}')

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
