"""A length of ground smooth rod."""

from solid_node.node import Length

from metamaquina2 import materials
from metamaquina2.part import ScadPart, curve


class SmoothRod(ScadPart):
    """One rod, standing on the origin and running up +Z.

    The design has no rod module -- it draws each rod inline where it
    is used -- so the cylinder is drawn here instead.  The length is
    declared without a default, because the X, Y and Z rods are three
    different parts to buy and cut and no length of them is the
    obvious one; the diameter is the 8 mm every rod on this machine
    runs, and the extruder's idler axle is the one part that redeclares
    it.
    """

    color = materials.METAL

    length = Length(min=0)
    diameter = Length(8.0, min=0)

    def render(self):
        return curve('cylinder', r=self.diameter / 2, h=self.length)
