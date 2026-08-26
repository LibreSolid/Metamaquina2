"""The tab that trips a Y endstop."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class YEndstopHolder(SheetPart):
    """A small plate standing off the platform's edge; one at each end
    of the travel, each hitting its microswitch on the bottom panel."""

    def profile(self):
        return machine.YEndstopHolder_face()
