"""A hex-head bolt, in whichever diameter and length is called for."""

from solid_node.node import Length

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import bolts


class Bolt(ScadPart):
    """One bolt: head on the XY plane, shank running down -Z.

    The design has an `M3x30`-style module per size, all of them
    forwarding to one `bolt(dia, length)`.  Here the size is declared
    instead, so every size reaches the artifact key and no two sizes
    can share a build.

    Neither has a default: a bolt with no size is not a part, and the
    thing that puts one in a hole is the thing that knows how long it
    has to be.
    """

    color = materials.METAL

    diameter = Length(min=0)
    length = Length(min=0)

    def render(self):
        return bolts.bolt(self.diameter, self.length)
