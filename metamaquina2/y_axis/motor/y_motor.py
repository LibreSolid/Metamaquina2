"""The Y motor on its holder."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.nema17_mount import Nema17Mount
from metamaquina2.params import (
    RightPanel_basewidth,
    bar_cut_length,
    feetheight,
)
from metamaquina2.y_axis.motor.motor_holder import YMotorHolder


class YMotor(AssemblyNode):
    """The Y stepper, its holder plate and its mounting bolts.

    The whole assembly hangs off the rear of the machine, turned on its
    side so the motor tucks in behind the rear bars, which is where the
    design puts it.
    """

    # where the holder plate meets the rear bars
    mount_height = 60 + feetheight + 12

    def __init__(self, *args, **kwargs):
        def mounted(node):
            return (node
                    .rotate(180, [0, 0, 1])
                    .rotate(-90, [0, 1, 0])
                    .translate([-7,
                                RightPanel_basewidth / 2 - bar_cut_length,
                                self.mount_height]))

        self.holder = mounted(YMotorHolder())
        self.motor = mounted(Nema17Mount()
                             .rotate(180, [1, 0, 0])
                             .rotate(-135, [0, 0, 1])
                             .translate([40, -60, -7])
                             .rotate(180, [1, 0, 0]))

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.holder, self.motor]
