"""M8 nylon-insert lock nut."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import nuts


class M8Locknut(ScadPart):
    """The nut that holds the hobbed bolt in the extruder."""

    color = materials.METAL

    def render(self):
        return nuts.M8_locknut()
