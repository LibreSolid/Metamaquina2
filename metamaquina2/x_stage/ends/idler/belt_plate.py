"""The side of the idler-side X end box that carries the idler."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class XEndIdlerBeltPlate(SheetPart):
    """The plate the idler shaft passes through."""

    def profile(self):
        return machine.XEndIdler_belt_face()
