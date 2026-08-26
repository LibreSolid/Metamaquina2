"""The right side panel."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class RightPanel(SheetPart):
    """The panel the power supply mounts to."""

    def profile(self):
        return machine.MachineRightPanel_face()
