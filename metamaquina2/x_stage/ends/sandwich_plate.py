"""The plate that traps an X end's Z bearings."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class XEndSandwichPlate(SheetPart):
    """One plate, cut with the bearings' own outline so they seat in
    it.  Both X ends use it."""

    def profile(self):
        return machine.xend_bearing_sandwich_face()
