"""NEMA 17 stepper motor."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import nema


class Nema17(ScadPart):
    """The motor itself, shaft pointing down -Z from the origin.

    Body, shaft and connector come from the design as one module, so
    the motor is one leaf: it is bought assembled and never taken
    apart.
    """

    color = materials.METAL

    def render(self):
        return nema.NEMA17()
