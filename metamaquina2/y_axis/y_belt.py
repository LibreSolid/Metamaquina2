"""The Y axis belt."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.params import (
    IdlerRadius,
    RightPanel_basewidth,
    bar_cut_length,
    base_bars_Zdistance,
    belt_width,
)
from metamaquina2.scad import machine


class YBelt(ScadPart):
    """One closed loop of GT2 belt, drawn around the three idlers it
    wraps: the front bar, the rear bar and the lower rear bar.

    The design's `YBelt` module bakes its position into the geometry;
    here the loop is the part and the position is the node's, so the
    belt could be moved without redrawing it.

    The loop is drawn in its own plane, where +x runs from the rear of
    the machine towards the front and +y runs upwards; the Y axis
    assembly stands it up.
    """

    color = materials.RUBBER

    def render(self):
        front_bar = RightPanel_basewidth / 2 - bar_cut_length
        rear_bar = -RightPanel_basewidth / 2 + bar_cut_length
        return machine.belt(
            bearings=[
                [front_bar, 0, IdlerRadius],
                [rear_bar, 0, IdlerRadius],
                [rear_bar + 30, -base_bars_Zdistance, IdlerRadius],
            ],
            belt_width=belt_width,
        )
