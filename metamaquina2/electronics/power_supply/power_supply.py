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

    unit = PowerSupplyUnit()
    box = PowerSupplyBox()
    washers = M3Washer().repeat(len(PowerSupply_mount_positions))
    bolts = Bolt(diameter=3, length=10).repeat(
        len(PowerSupply_mount_positions))

    def render(self):
        drop = -thickness - m3_washer_thickness
        for mount, (x, y) in enumerate(PowerSupply_mount_positions):
            at = [PowerSupply_width - x, y, drop]
            self.washers[mount].translate(at)
            self.bolts[mount].rotate(180, [1, 0, 0]).translate(at)
