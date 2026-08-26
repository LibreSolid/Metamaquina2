"""The short smooth rod the extruder idler bearing turns on."""

from metamaquina2.hardware.smooth_rod import SmoothRod


class IdlerAxle(SmoothRod):
    """A 30 mm length of 7.8 mm rod.

    Not an M8 bolt: it is undersized so the bearing runs on ground
    rod rather than on a thread.
    """

    length = 30
    diameter = 7.8

    def __init__(self, **kwargs):
        super().__init__(self.length, self.diameter, **kwargs)
