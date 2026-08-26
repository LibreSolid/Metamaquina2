"""The left side panel."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class LeftPanel(SheetPart):
    """The panel the electronics and the Z endstops mount to.

    Cut from the same stock as the right panel but a different part:
    it carries the RAMBo, the cable clips and both Z endstops, and its
    profile has the holes for all of them.
    """

    def profile(self):
        return machine.MachineLeftPanel_face()
