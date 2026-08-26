"""M3 nylon-insert lock nut."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import nuts


class M3Locknut(ScadPart):
    """The nut used everywhere a joint must not shake loose."""

    color = materials.METAL

    def render(self):
        return nuts.M3_locknut()
