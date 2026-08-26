"""The bar the spool turns on."""

from metamaquina2 import materials
from metamaquina2.part import SheetPart
from metamaquina2.params import SpoolHolder_bar_length
from metamaquina2.scad import spool_holder


class SpoolHolderBar(SheetPart):
    """A length of M8 threaded bar, drawn the way the design draws it:
    its circular section extruded along its length."""

    color = materials.THREADED_METAL
    sheet_thickness = SpoolHolder_bar_length

    def profile(self):
        return spool_holder.FilamentSpoolHolder_bar_face()
