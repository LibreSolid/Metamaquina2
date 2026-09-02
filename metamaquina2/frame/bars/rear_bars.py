"""The two threaded bars across the back of the machine."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.bars.bar_clamp_mount import BarClampMount
from metamaquina2.frame.bars.belt_idler import BeltIdler
from metamaquina2.frame.bars.front_bars import place_bar, place_caps
from metamaquina2.frame.bars.nut_cap import NutCap
from metamaquina2.hardware.threaded_rod import ThreadedRod
from metamaquina2.params import (
    RightPanel_basewidth,
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

    upper_bar = ThreadedRod(length=horiz_bars_length)
    upper_caps = NutCap().repeat(2)
    rod_clamps = BarClampMount().repeat(2)
    upper_idler = BeltIdler(spaced=True)
    lower_bar = ThreadedRod(length=horiz_bars_length)
    lower_caps = NutCap().repeat(2)
    lower_idler = BeltIdler(spaced=True)

    def render(self):
        rear = RightPanel_basewidth / 2 - bar_cut_length
        upper_z = base_bars_Zdistance + base_bars_height

        place_bar(self.upper_bar, rear, upper_z)
        place_caps(self.upper_caps, rear, upper_z)
        for clamp, side in zip(self.rod_clamps, (-1, 1)):
            clamp.translate([side * Y_rods_distance / 2, rear, upper_z])
        self.upper_idler.translate([0, rear, upper_z])

        lower_y = rear - self.lower_bar_setback
        place_bar(self.lower_bar, lower_y, base_bars_height)
        place_caps(self.lower_caps, lower_y, base_bars_height)
        self.lower_idler.translate([0, lower_y, base_bars_height])
