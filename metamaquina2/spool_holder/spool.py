"""A reel of filament."""

from metamaquina2 import materials
from metamaquina2.params import (
    filament_diameter,
    spool_bore,
    spool_diameter,
    spool_width,
)
from metamaquina2.part import ScadPart, curve


class FilamentSpool(ScadPart):
    """A full reel, as the stock wound under its outermost layer.

    Not a part of the machine but of what it consumes; the design draws
    it to show the stand loaded, and draws it as a plain tube, which is
    an honest way to draw two hundred turns in four layers and no use
    at all once one of them is a strand.

    So the tube here stops one stock diameter short of the design's own
    reel diameter and `filament` lays that last layer on it as the
    strand it is.  The two together still come to the 160 the design
    draws: what changed is that the outside of the reel is now made of
    turns.
    """

    color = materials.ABS

    #: What the design draws, from the bare numbers in `FilamentSpool()`.
    outer_diameter = spool_diameter
    bore_diameter = spool_bore
    width = spool_width

    #: What is left for the tube once the outermost layer is drawn.
    wound_diameter = outer_diameter - 2 * filament_diameter

    def render(self):
        section = (curve('circle', r=self.wound_diameter / 2)
                   - curve('circle', r=self.bore_diameter / 2))
        return section.linear_extrude(self.width)
