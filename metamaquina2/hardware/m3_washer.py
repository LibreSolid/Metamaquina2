"""M3 flat washer."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import washers


class M3Washer(ScadPart):
    """A washer for an M3 bolt, sitting on the XY plane."""

    color = materials.METAL

    def render(self):
        return washers.M3_washer()
