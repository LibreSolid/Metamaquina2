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

from solid_node.simulation import Sim
from solid_node.test import TestCase

from metamaquina2.params import (
    BuildVolume_X,
    BuildVolume_Y,
    XCarPosition,
    YCarPosition,
    ZCarPosition,
)


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

    def _is_on(self, bearing, rod):
        """Is this bearing threaded onto this rod?"""
        try:
            self.assertClose(rod, bearing, self.ON_THE_ROD)
        except AssertionError:
            return False
        return True
