"""The heated bed PCB."""

from metamaquina2 import materials
from metamaquina2.part import SheetPart
from metamaquina2.params import heated_bed_pcb_thickness
from metamaquina2.scad import heated_bed


class HeatedBedPcb(SheetPart):
    """The heater itself: a PCB whose copper is the heating element.

    A board is a part cut from flat stock like any other, so it is
    authored the same way -- its outline, and the thickness it is made
    in.
    """

    color = materials.PCB
    sheet_thickness = heated_bed_pcb_thickness

    def profile(self):
        return heated_bed.heated_bed_pcb_curves()
