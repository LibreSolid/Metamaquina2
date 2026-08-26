"""The power supply, its box and its mounting bolts."""

from solid_node.node import AssemblyNode

from metamaquina2.electronics.power_supply.box import PowerSupplyBox
from metamaquina2.electronics.power_supply.unit import PowerSupplyUnit
from metamaquina2.hardware.bolt import Bolt
from metamaquina2.hardware.m3_washer import M3Washer
from metamaquina2.params import (
    PowerSupply_mount_positions,
    PowerSupply_width,
    m3_washer_thickness,
    thickness,
)


class PowerSupply(AssemblyNode):
    """Everything that hangs off the right panel to power the machine.

    Drawn in the right panel's plane; the panel's frame stands it up.
    """

    def __init__(self, *args, **kwargs):
        self.unit = PowerSupplyUnit()
        self.box = PowerSupplyBox()

        drop = -thickness - m3_washer_thickness
        self.washers = []
        self.bolts = []
        for x, y in PowerSupply_mount_positions:
            at = [PowerSupply_width - x, y, drop]
            self.washers.append(M3Washer().translate(at))
            self.bolts.append(
                Bolt(3, 10).rotate(180, [1, 0, 0]).translate(at))

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.unit, self.box] + self.washers + self.bolts
