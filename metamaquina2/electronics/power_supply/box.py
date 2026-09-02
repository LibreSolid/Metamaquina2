"""The lasercut box that encloses the power supply."""

from solid_node.node import AssemblyNode

from metamaquina2.electronics.power_supply.box_plate import (
    PowerSupplyBoxPlate)
from metamaquina2.electronics.power_supply.female_connector import (
    FemaleConnector)
from metamaquina2.params import (
    PSU_Female_border_height,
    PowerSupplyBox_height,
    PowerSupply_bottom_offset,
    PowerSupply_sheet_thickness,
    PowerSupply_thickness,
    PowerSupply_width,
    thickness,
)


class PowerSupplyBox(AssemblyNode):
    """Four plates around the supply, with the mains inlet in the back.

    It is a guard, not a chassis: the supply is bolted to the panel and
    this keeps fingers off its terminals.

    The four plates are four different profiles, so each is its own
    declaration; `PowerSupplyBoxPlate` names which by a string and so
    keeps its constructor.
    """

    side = PowerSupplyBoxPlate('side')
    bottom = PowerSupplyBoxPlate('bottom')
    front = PowerSupplyBoxPlate('front')
    back = PowerSupplyBoxPlate('back')
    inlet = FemaleConnector()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        base = -PowerSupplyBox_height + PowerSupply_bottom_offset

        self.side.translate(
            [thickness, base, PowerSupply_thickness - thickness])

        (self.bottom
         .rotate(90, [1, 0, 0])
         .translate([thickness, base + thickness, 0]))

        (self.front
         .rotate(-90, [0, 1, 0])
         .translate([thickness, base, 0]))

        (self.back
         .rotate(-90, [0, 1, 0])
         .translate([PowerSupply_width - PowerSupply_sheet_thickness,
                     base, 0]))

        (self.inlet
         .rotate(180, [1, 0, 0])
         .rotate(90, [0, 0, 1])
         .translate([PowerSupply_thickness - thickness
                     - PSU_Female_border_height / 2,
                     (PowerSupplyBox_height
                      - PowerSupply_bottom_offset) / 2,
                     0])
         .rotate(-90, [0, 1, 0])
         .translate([PowerSupply_width - PowerSupply_sheet_thickness,
                     base, 0]))
