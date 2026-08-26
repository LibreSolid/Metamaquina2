"""A reel of filament."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart, curve


class FilamentSpool(ScadPart):
    """A full spool, as a plain tube.

    Not a part of the machine but of what it consumes; the design draws
    it to show the stand loaded.  Its dimensions are written inline in
    the design's own module, and repeated here.
    """

    color = materials.ABS

    outer_diameter = 160
    bore_diameter = 35
    width = 160

    def render(self):
        section = (curve('circle', r=self.outer_diameter / 2)
                   - curve('circle', r=self.bore_diameter / 2))
        return section.linear_extrude(self.width)
