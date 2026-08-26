"""The two vertical threaded bars that lift the X stage."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.threaded_rod import ThreadedRod
from metamaquina2.params import (
    BottomPanel_zoffset,
    XZStage_offset,
    Z_bar_length,
    lm8uu_diameter,
    machine_x_dim,
    motor_shaft_length,
    thickness,
    z_rod_z_bar_distance,
)


class ZBars(AssemblyNode):
    """Two M8 threaded bars, each driven by its own motor below it.

    They start at the top of the motor shaft, where the coupling joins
    them, and run to the top of the machine.
    """

    def __init__(self, *args, **kwargs):
        offset = (machine_x_dim / 2 - thickness - lm8uu_diameter / 2
                  - z_rod_z_bar_distance)
        self.bars = [
            ThreadedRod(Z_bar_length).translate(
                [side * offset, -XZStage_offset,
                 BottomPanel_zoffset + motor_shaft_length])
            for side in (-1, 1)
        ]
        super().__init__(*args, **kwargs)

    def render(self):
        return self.bars
