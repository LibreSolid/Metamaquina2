"""The top panel."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class TopPanel(SheetPart):
    """The panel that ties the two side panels together at the top and
    carries the wiring pass-through for the extruder."""

    def profile(self):
        return machine.MachineTopPanel_face()
