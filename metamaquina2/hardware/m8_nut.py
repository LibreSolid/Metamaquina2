"""M8 hex nut."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import nuts


class M8Nut(ScadPart):
    """A plain M8 hex nut, sitting on the XY plane."""

    color = materials.METAL

    def render(self):
        return nuts.M8_nut()
