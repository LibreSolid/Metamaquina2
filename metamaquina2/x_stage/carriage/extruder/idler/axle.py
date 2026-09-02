"""The short smooth rod the extruder idler bearing turns on."""

from solid_node.node import Length

from metamaquina2.hardware.smooth_rod import SmoothRod


class IdlerAxle(SmoothRod):
    """A 30 mm length of 7.8 mm rod.

    Not an M8 bolt: it is undersized so the bearing runs on ground
    rod rather than on a thread.  Both numbers are the rod's own
    parameters redeclared, so the part states what it is and nothing
    has to construct it with arguments.
    """

    length = Length(30.0, min=0)
    diameter = Length(7.8, min=0)
