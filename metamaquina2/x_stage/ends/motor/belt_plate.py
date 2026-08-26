"""The side of the motor-side X end box that carries the X motor."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class XEndMotorBeltPlate(SheetPart):
    """The plate the X stepper bolts through."""

    def profile(self):
        return machine.XEndMotor_belt_face()
