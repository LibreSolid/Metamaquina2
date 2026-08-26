"""The power connector on the RAMBo board."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import rambo


class PsuConnector(ScadPart):
    """The screw terminal the power supply wires land on."""

    color = materials.NYLON

    def render(self):
        return rambo.PSU_connector()
