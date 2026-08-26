"""A length of ground smooth rod."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart, curve


class SmoothRod(ScadPart):
    """One rod, standing on the origin and running up +Z.

    The design has no rod module -- it draws each rod inline where it
    is used -- so the cylinder is drawn here instead.  The length is a
    constructor argument, because the X, Y and Z rods are three
    different parts to buy and cut.
    """

    color = materials.METAL

    def __init__(self, length, diameter=8, **kwargs):
        self.length = length
        self.diameter = diameter
        super().__init__(length, diameter, **kwargs)

    def render(self):
        return curve('cylinder', r=self.diameter / 2, h=self.length)
