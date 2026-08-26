"""The outer face of the motor-side X end."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class XEndMotorBackPlate(SheetPart):
    """The plate facing out of the machine, cut with the slots the two
    Z bearings ride in."""

    def profile(self):
        return machine.XEndMotor_back_face()
