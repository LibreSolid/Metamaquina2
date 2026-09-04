"""The idler the X belt turns around."""

from solid_node.node import AssemblyNode
from solid_node.parameters import Length

from metamaquina2.hardware.bearing_608zz import Bearing608zz
from metamaquina2.hardware.smooth_rod import SmoothRod


class XIdlerPulley(AssemblyNode):
    """A 608 bearing on a short shaft.

    A plain bearing rather than a toothed pulley: the belt runs on it
    back-side out, so it only needs to be round.
    """

    shaft_length = Length(80.0, min=0)

    shaft = SmoothRod(length=shaft_length)
    bearing = Bearing608zz()

    def render(self):
        self.shaft.translate([0, 0, -self.shaft_length / 2])
