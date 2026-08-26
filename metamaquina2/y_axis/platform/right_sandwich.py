"""The right bearing sandwich plate of the Y platform."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class RightBearingSandwich(SheetPart):
    """The plate that traps the two right-hand Y bearings."""

    def profile(self):
        return machine.YPlatform_right_sandwich_face()
