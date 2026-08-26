"""The flexible coupling between a Z motor shaft and a Z bar."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import coupling


class ShaftCoupling(ScadPart):
    """Bought as one piece, so one leaf."""

    color = materials.ABS

    def render(self):
        return coupling.coupling()
