"""The arc panel that closes the back of the machine."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class ArcPanel(SheetPart):
    """The curved rear panel, joined to the side panels by t-slots."""

    def profile(self):
        return machine.MachineArcPanel_face()
