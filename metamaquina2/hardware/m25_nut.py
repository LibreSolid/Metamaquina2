"""M2.5 hex nut, the one the microswitches mount with."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import nuts


class M25Nut(ScadPart):
    """A plain M2.5 hex nut, sitting on the XY plane."""

    color = materials.METAL

    def render(self):
        return nuts.M25_nut()
