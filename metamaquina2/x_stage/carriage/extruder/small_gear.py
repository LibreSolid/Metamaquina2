"""The small printed gear on the extruder motor shaft."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import small_gear


class MotorGear(ScadPart):
    """11 teeth, pressed onto the stepper shaft."""

    color = materials.ABS
    teeth = 11

    def render(self):
        return small_gear.motor_gear(teeth=self.teeth)
