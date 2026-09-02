"""The two threaded bars across the front of the machine."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.bars.bar_clamp_mount import BarClampMount
from metamaquina2.frame.bars.belt_idler import BeltIdler
from metamaquina2.frame.bars.nut_cap import NutCap
from metamaquina2.hardware.threaded_rod import ThreadedRod
from metamaquina2.params import (
    RightPanel_basewidth,
    SidePanels_distance,
    Y_rods_distance,
    bar_cut_length,
    base_bars_Zdistance,
    base_bars_height,
    horiz_bars_length,
)


def place_bar(bar, y, z):
    """Lay a bar across the machine at (y, z)."""
    return (bar
            .translate([0, 0, -horiz_bars_length / 2])
            .rotate(90, [0, 1, 0])
            .translate([0, y, z]))


def place_caps(caps, y, z):
    """Cap both ends of a bar where it leaves the two side panels."""
    caps[0].translate([SidePanels_distance / 2, 0, z]).translate([0, y, 0])
    (caps[1]
     .rotate(180, [0, 0, 1])
     .translate([-SidePanels_distance / 2, 0, z])
     .translate([0, y, 0]))


class FrontBars(AssemblyNode):
    """The front pair of horizontal M8 bars and what rides on them.

    The upper bar does the work: it carries the front ends of both Y
    rods through their bar clamps and the front Y belt idler.  The
    lower bar, 30 mm further back and lower down, only stiffens the
    frame, so it has nothing on it but its end nuts.
    """

    # how far back the lower bar sits from the upper one
    lower_bar_setback = 30

    upper_bar = ThreadedRod(length=horiz_bars_length)
    upper_caps = NutCap().repeat(2)
    rod_clamps = BarClampMount().repeat(2)
    idler = BeltIdler()
    lower_bar = ThreadedRod(length=horiz_bars_length)
    lower_caps = NutCap().repeat(2)

    def render(self):
        front = -RightPanel_basewidth / 2 + bar_cut_length
        upper_z = base_bars_Zdistance + base_bars_height

        place_bar(self.upper_bar, front, upper_z)
        place_caps(self.upper_caps, front, upper_z)
        for clamp, side in zip(self.rod_clamps, (-1, 1)):
            clamp.translate([side * Y_rods_distance / 2, front, upper_z])
        self.idler.translate([0, front, upper_z])

        lower_y = front + self.lower_bar_setback
        place_bar(self.lower_bar, lower_y, base_bars_height)
        place_caps(self.lower_caps, lower_y, base_bars_height)
