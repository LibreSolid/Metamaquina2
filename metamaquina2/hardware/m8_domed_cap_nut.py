"""M8 domed cap nut."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import domed_cap_nuts


class M8DomedCapNut(ScadPart):
    """The finished end of a threaded bar where it leaves a side panel."""

    color = materials.METAL

    def render(self):
        return domed_cap_nuts.M8_domed_cap_nut()
