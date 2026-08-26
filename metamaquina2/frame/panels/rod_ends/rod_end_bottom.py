"""The plate that locates a Z rod at the bottom of the machine."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class RodEndBottom(SheetPart):
    """One of the two lower rod-end plates, under the bottom panel."""

    def profile(self):
        return machine.RodEndBottom_face()
