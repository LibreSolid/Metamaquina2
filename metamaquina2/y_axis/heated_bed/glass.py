"""The glass sheet the prints are made on."""

from solid2 import cube

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.params import glass_h, glass_w, heated_bed_glass_thickness


class HeatedBedGlass(ScadPart):
    """A plain rectangle of glass, clipped over the heated bed.

    The design draws it inline as a cube, so the cube is drawn here;
    unlike the design's version it stands on its own origin, and the
    heated bed assembly puts it on top of the board.
    """

    color = materials.GLASS

    def render(self):
        return cube([glass_w, glass_h, heated_bed_glass_thickness])
