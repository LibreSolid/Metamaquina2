"""The inner face of an X end."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class XEndFrontPlate(SheetPart):
    """The plate facing into the machine.  Both X ends use it."""

    def profile(self):
        return machine.XEnd_front_face()
