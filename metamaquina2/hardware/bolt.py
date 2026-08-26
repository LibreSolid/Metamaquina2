"""A hex-head bolt, in whichever diameter and length is called for."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import bolts


class Bolt(ScadPart):
    """One bolt: head on the XY plane, shank running down -Z.

    The design has an `M3x30`-style module per size, all of them
    forwarding to one `bolt(dia, length)`.  Here the size is a
    constructor argument instead, so every size reaches the artifact
    key and no two sizes can share a build.
    """

    color = materials.METAL

    def __init__(self, diameter, length, **kwargs):
        self.diameter = diameter
        self.length = length
        super().__init__(diameter, length, **kwargs)

    def render(self):
        return bolts.bolt(self.diameter, self.length)
