"""An acrylic spacer beside the extruder idler bearing."""

from metamaquina2 import materials
from metamaquina2.part import SheetPart
from metamaquina2.scad import extruder


class IdlerSpacer(SheetPart):
    """A 5 mm acrylic ring that keeps the idler bearing centred
    between the side plates."""

    color = materials.ACRYLIC
    sheet_thickness = 5

    def profile(self):
        return extruder.idler_spacer_face()
