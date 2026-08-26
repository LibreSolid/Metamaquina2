"""The two Z motors, hanging under the bottom panel."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.nema17_mount import Nema17Mount
from metamaquina2.params import (
    BottomPanel_zoffset,
    XZStage_offset,
    Z_rods_distance,
    z_rod_z_bar_distance,
)


class ZMotors(AssemblyNode):
    """One stepper per side, turned to face each other.

    Both hang shaft-up through the bottom panel, each directly under
    the threaded bar it turns.
    """

    def __init__(self, *args, **kwargs):
        offset = Z_rods_distance / 2 - z_rod_z_bar_distance
        self.motors = [
            Nema17Mount()
            .rotate(side * 90, [0, 0, 1])
            .rotate(180, [1, 0, 0])
            .translate([side * offset, -XZStage_offset, BottomPanel_zoffset])
            for side in (1, -1)
        ]
        super().__init__(*args, **kwargs)

    def render(self):
        return self.motors
