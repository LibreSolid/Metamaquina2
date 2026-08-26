"""The electronics: controller, power supply, endstops and cable clips."""

from solid_node.node import AssemblyNode

from metamaquina2 import frames
from metamaquina2.electronics.cable_clips import CableClips
from metamaquina2.electronics.endstops.endstops import Endstops
from metamaquina2.electronics.power_supply.power_supply import PowerSupply
from metamaquina2.electronics.rambo.rambo import Rambo
from metamaquina2.params import (
    HIQUA_POWERSUPPLY,
    RAMBo_x,
    RAMBo_y,
    powersupply_Xposition,
    powersupply_Yposition,
    thickness,
)


class Electronics(AssemblyNode):
    """What a builder fits after the frame and the axes are together.

    The controller goes on the left panel, the power supply on the
    right, the endstops where each axis ends, and the clips wherever
    the loom needs holding down.  The power supply is fitted only when
    the design is configured for the Hiqua brick this machine ships
    with.
    """

    def __init__(self, *args, **kwargs):
        self.rambo = frames.left_panel(
            Rambo().translate([RAMBo_x, RAMBo_y, thickness]))

        self.endstops = Endstops()
        self.cable_clips = CableClips()

        self.power_supply = None
        if HIQUA_POWERSUPPLY:
            self.power_supply = frames.right_panel(
                PowerSupply()
                .rotate(180, [0, 1, 0])
                .translate([powersupply_Xposition,
                            powersupply_Yposition, 0]))

        super().__init__(*args, **kwargs)

    def render(self):
        children = [self.rambo, self.endstops, self.cable_clips]
        if self.power_supply is not None:
            children.append(self.power_supply)
        return children
