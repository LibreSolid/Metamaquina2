"""The blank side of the motor-side X end box."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class XEndMotorPlainPlate(SheetPart):
    """The side of the box away from the belt."""

    def profile(self):
        return machine.XEndMotor_plain_face()
