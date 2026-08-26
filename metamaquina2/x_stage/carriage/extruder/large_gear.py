"""The big printed gear on the hobbed bolt."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import large_gear


class ExtruderGear(ScadPart):
    """37 teeth, driven by the 11-tooth motor gear: the reduction that
    turns motor speed into filament force."""

    color = materials.ABS
    teeth = 37

    def render(self):
        return large_gear.extruder_gear(teeth=self.teeth)
