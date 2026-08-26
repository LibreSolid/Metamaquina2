"""M8 flat washer."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import washers


class M8Washer(ScadPart):
    """A washer for an M8 bar or bolt, sitting on the XY plane."""

    color = materials.METAL

    def render(self):
        return washers.M8_washer()
