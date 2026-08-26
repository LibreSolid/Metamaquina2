"""The mains inlet on the back of the power supply box."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import power_supply


class FemaleConnector(ScadPart):
    """An IEC-style panel inlet, snapped into the back plate."""

    color = materials.ABS

    def render(self):
        return power_supply.PowerSupply_FemaleConnector()
