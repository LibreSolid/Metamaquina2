"""The couplings that join each Z motor shaft to its threaded bar."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.shaft_coupling import ShaftCoupling
from metamaquina2.params import (
    BottomPanel_zoffset,
    XZStage_offset,
    coupling_shaft_depth,
    lm8uu_diameter,
    machine_x_dim,
    motor_shaft_length,
    thickness,
    z_rod_z_bar_distance,
)


class ZCouplings(AssemblyNode):
    """Two flexible couplings, one per side.

    They sit where the motor shaft ends and the threaded bar begins,
    and they are what lets the bar be slightly out of true with the
    motor without binding the axis.
    """

    def __init__(self, *args, **kwargs):
        offset = (machine_x_dim / 2 - thickness - lm8uu_diameter / 2
                  - z_rod_z_bar_distance)
        height = (BottomPanel_zoffset + motor_shaft_length
                  - coupling_shaft_depth)
        self.couplings = [
            ShaftCoupling().translate([side * offset, -XZStage_offset, height])
            for side in (-1, 1)
        ]
        super().__init__(*args, **kwargs)

    def render(self):
        return self.couplings
