"""The bottom panel."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class BottomPanel(SheetPart):
    """The panel spanning the base of the machine, under the Y axis,
    carrying the two Y endstops."""

    def profile(self):
        return machine.MachineBottomPanel_face()
