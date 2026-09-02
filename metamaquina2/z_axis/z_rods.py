"""The two vertical smooth rods that guide the X stage."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.smooth_rod import SmoothRod
from metamaquina2.params import (
    BottomPanel_zoffset,
    XZStage_offset,
    Z_rod_length,
    lm8uu_diameter,
    machine_x_dim,
    thickness,
)


class ZRods(AssemblyNode):
    """Two 8 mm rods standing at the far left and right of the machine.

    These take the load; the threaded bars beside them only lift.  Each
    is capped top and bottom by a rod-end plate on the frame.
    """

    rods = SmoothRod(length=Z_rod_length).repeat(2)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        offset = machine_x_dim / 2 - thickness - lm8uu_diameter / 2
        for rod, side in zip(self.rods, (-1, 1)):
            rod.translate(
                [side * offset, -XZStage_offset, BottomPanel_zoffset])
