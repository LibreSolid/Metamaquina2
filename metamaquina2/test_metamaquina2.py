"""Contracts the assembly has to keep.

These check the thing this layer is actually responsible for.  The
geometry of each part comes from the OpenSCAD design and was correct
before this package existed; what is new here is where every part is
put.  So the tests ask whether parts that must be on the same rod are
on it, and whether the axes reach the travel the machine claims.

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

from solid_node.test import TestCase

from metamaquina2.params import BuildVolume_X, BuildVolume_Y


class Metamaquina2Test(TestCase):

    # An LM8UU is 15 mm across on an 8 mm rod, so every point on the
    # bearing is within 3.5 mm of the rod it is threaded onto.  Any rod
    # it is NOT on is tens of millimetres away, so this distance
    # separates the two cases with room to spare, and does it without
    # depending on how a nominal slip fit tessellates.
    ON_THE_ROD = 6

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

    def _is_on(self, bearing, rod):
        """Is this bearing threaded onto this rod?"""
        try:
            self.assertClose(rod, bearing, self.ON_THE_ROD)
        except AssertionError:
            return False
        return True
