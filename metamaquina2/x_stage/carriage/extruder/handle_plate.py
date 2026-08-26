"""The lasercut lever that releases the extruder idler."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import extruder


class HandlePlate(SheetPart):
    """One plate, with the Metamaquina M cut into it."""

    def profile(self):
        return extruder.handle_face()
