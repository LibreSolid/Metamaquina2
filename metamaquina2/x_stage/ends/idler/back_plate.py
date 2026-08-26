"""The outer face of the idler-side X end."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class XEndIdlerBackPlate(SheetPart):
    """The plate facing out of the machine on the right-hand end."""

    def profile(self):
        return machine.XEndIdler_back_face()
