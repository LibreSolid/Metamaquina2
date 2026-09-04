"""The electronics: controller, power supply, endstops and cable clips."""

from solid_node.node import AssemblyNode
from solid_node.parameters import Flag

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
    the loom needs holding down.

    The power supply is the one part of this machine that is fitted or
    not: the design configures it with `HIQUA_POWERSUPPLY`, which is
    the brick this machine ships with, and a machine built without it
    is a machine with a different mass and a shorter bill of
    materials.  So it is a flag the root passes down and an `omit()`,
    not a `None` the render has to step around.
    """

    power_supply_fitted = Flag(HIQUA_POWERSUPPLY)

    rambo = Rambo()
    endstops = Endstops()
    cable_clips = CableClips()
    power_supply = PowerSupply()

    def render(self):
        """Fit the controller and, on a machine that has one, the
        supply.

        Nothing here moves, so the whole of it is the machine at rest:
        where each part goes, and whether the supply is there at all.
        Presence belongs here and nowhere else -- structure is decided
        at rest, and `simulate` may not omit.
        """
        frames.left_panel(
            self.rambo.translate([RAMBo_x, RAMBo_y, thickness]))

        if self.power_supply_fitted:
            frames.right_panel(
                self.power_supply
                .rotate(180, [0, 1, 0])
                .translate([powersupply_Xposition,
                            powersupply_Yposition, 0]))
        else:
            self.power_supply.omit()
