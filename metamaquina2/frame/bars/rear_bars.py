"""The two threaded bars across the back of the machine."""

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


class RearBars(AssemblyNode):
    """The rear pair of horizontal M8 bars and what rides on them.

    The mirror of the front pair, except that both rear bars carry a
    belt idler: the Y belt runs back along the machine, down around
    the lower rear bar and forward again, so the lower bar is a
    working bar here and not just a stiffener.  Both rear idlers need
    the extra washer and nut that clears the panel behind them.
    """

    lower_bar_setback = 30

    def __init__(self, *args, **kwargs):
        rear = RightPanel_basewidth / 2 - bar_cut_length

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
        self.upper_bar = bar().translate([0, rear, upper_z])
        self.upper_caps = [cap.translate([0, rear, 0])
                           for cap in caps(upper_z)]
        self.rod_clamps = [
            BarClampMount().translate(
                [side * Y_rods_distance / 2, rear, upper_z])
            for side in (-1, 1)
        ]
        self.upper_idler = BeltIdler(spaced=True).translate(
            [0, rear, upper_z])

        lower_y = rear - self.lower_bar_setback
        self.lower_bar = bar().translate([0, lower_y, base_bars_height])
        self.lower_caps = [cap.translate([0, lower_y, 0])
                           for cap in caps(base_bars_height)]
        self.lower_idler = BeltIdler(spaced=True).translate(
            [0, lower_y, base_bars_height])

        super().__init__(*args, **kwargs)

    def render(self):
        return ([self.upper_bar] + self.upper_caps + self.rod_clamps
                + [self.upper_idler, self.lower_bar] + self.lower_caps
                + [self.lower_idler])
