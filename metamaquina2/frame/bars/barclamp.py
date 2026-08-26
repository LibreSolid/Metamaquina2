"""The printed clamp that fixes a Y rod to a frame bar."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import bar_clamp


class BarClamp(ScadPart):
    """One printed bar clamp.

    Four of these carry the Y axis: each grips a horizontal threaded
    bar and holds one end of a Y rod parallel to it.
    """

    color = materials.ABS

    def render(self):
        return bar_clamp.barclamp()
