"""The small printed gear on the extruder motor shaft."""

from solid_node.node import Count

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import small_gear


class MotorGear(ScadPart):
    """11 teeth, pressed onto the stepper shaft."""

    color = materials.ABS
    teeth = Count(11, min=1)

    def render(self):
        return small_gear.motor_gear(teeth=self.teeth)
