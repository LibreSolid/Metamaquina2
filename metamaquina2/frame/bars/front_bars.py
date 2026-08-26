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


class FrontBars(AssemblyNode):
    """The front pair of horizontal M8 bars and what rides on them.

    The upper bar does the work: it carries the front ends of both Y
    rods through their bar clamps and the front Y belt idler.  The
    lower bar, 30 mm further back and lower down, only stiffens the
    frame, so it has nothing on it but its end nuts.
    """

    # how far back the lower bar sits from the upper one
    lower_bar_setback = 30

    def __init__(self, *args, **kwargs):
        front = -RightPanel_basewidth / 2 + bar_cut_length

        def bar():
            return (ThreadedRod(horiz_bars_length)
                    .translate([0, 0, -horiz_bars_length / 2])
                    .rotate(90, [0, 1, 0]))

        def caps(z):
            right = NutCap().translate([SidePanels_distance / 2, 0, z])
            left = (NutCap()
                    .rotate(180, [0, 0, 1])
                    .translate([-SidePanels_distance / 2, 0, z]))
            return [right, left]

        upper_z = base_bars_Zdistance + base_bars_height
        self.upper_bar = bar().translate([0, front, upper_z])
        self.upper_caps = [cap.translate([0, front, 0])
                           for cap in caps(upper_z)]
        self.rod_clamps = [
            BarClampMount().translate(
                [side * Y_rods_distance / 2, front, upper_z])
            for side in (-1, 1)
        ]
        self.idler = BeltIdler().translate([0, front, upper_z])

        lower_y = front + self.lower_bar_setback
        self.lower_bar = bar().translate([0, lower_y, base_bars_height])
        self.lower_caps = [cap.translate([0, lower_y, 0])
                           for cap in caps(base_bars_height)]

        super().__init__(*args, **kwargs)

    def render(self):
        return ([self.upper_bar] + self.upper_caps + self.rod_clamps
                + [self.idler, self.lower_bar] + self.lower_caps)
