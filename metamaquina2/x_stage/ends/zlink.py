"""The printed link between an X end and its Z threaded bar."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import zlink


class ZLink(ScadPart):
    """One Z link.

    It captures a nut on the threaded bar and pushes it against a
    spring, so backlash in the Z axis is taken up rather than left to
    show up in the print.
    """

    color = materials.ABS

    def render(self):
        return zlink.ZLink()
