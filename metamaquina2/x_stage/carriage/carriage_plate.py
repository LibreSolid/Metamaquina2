"""The main plate of the X carriage."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class XCarriagePlate(SheetPart):
    """The plate the extruder bolts onto and the bearings hang under."""

    def profile(self):
        return machine.XCarriage_bottom_face()
