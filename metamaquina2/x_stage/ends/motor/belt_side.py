"""The belt side of the motor X end: its plate and the X motor."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.nema17_mount import Nema17Mount
from metamaquina2.params import XEnd_box_size, XMotor_height, thickness
from metamaquina2.x_stage.ends.motor.belt_plate import XEndMotorBeltPlate


class XEndMotorBeltSide(AssemblyNode):
    """The plate and the motor bolted to it, in the plate's own plane.

    The design also draws a GT2 pulley on the shaft here.  Its module
    is an empty stub -- the design never modelled the pulley -- so
    there is no part to make a node of, and the belt in the assembly
    above wraps a radius rather than a tooth form.
    """

    def __init__(self, *args, **kwargs):
        self.plate = XEndMotorBeltPlate().translate([0, thickness, 0])
        self.motor = (Nema17Mount()
                      .rotate(-180, [1, 0, 0])
                      .translate([XEnd_box_size / 2, XMotor_height, 0]))
        super().__init__(*args, **kwargs)

    def render(self):
        return [self.plate, self.motor]
