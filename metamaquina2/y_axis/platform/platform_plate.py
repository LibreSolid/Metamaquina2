"""The Y platform plate."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class YPlatformPlate(SheetPart):
    """The big sheet the heated bed sits on and the bearings hang from."""

    def profile(self):
        return machine.YPlatform_face()
