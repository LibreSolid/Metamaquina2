"""A mechanical endstop microswitch."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import endstop


class Microswitch(ScadPart):
    """A KW11-3Z lever microswitch.

    Bought as one part, so one leaf -- although the design draws the
    body and the lever as two separate shapes, which is what they are
    on the real switch.
    """

    color = materials.RUBBER

    def render(self):
        return endstop.mechanical_switch()
