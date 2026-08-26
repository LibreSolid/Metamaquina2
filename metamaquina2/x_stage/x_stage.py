"""The X stage: the whole beam the Z axis lifts."""

from solid_node.node import AssemblyNode

from metamaquina2.params import (
    XEnd_extra_width,
    XPlatform_width,
    belt_offset,
    thickness,
)
from metamaquina2.x_stage.carriage.x_carriage import XCarriage
from metamaquina2.x_stage.ends.idler.x_end_idler import XEndIdler
from metamaquina2.x_stage.ends.motor.x_end_motor import XEndMotor
from metamaquina2.x_stage.platform_plate import XPlatformPlate
from metamaquina2.x_stage.x_belt import XBelt
from metamaquina2.x_stage.x_rods import XRods


class XStage(AssemblyNode):
    """The X beam and everything on it.

    A box at each end riding the Z rods, two smooth rods between them,
    a carriage on those rods, and a belt from the motor at one end to
    the idler at the other.  The whole assembly goes up and down as one
    thing, which is why it is one assembly.
    """

    def __init__(self, *args, **kwargs):
        self.end_motor = XEndMotor()
        self.end_idler = XEndIdler()
        self.carriage = XCarriage()
        self.plate = XPlatformPlate()
        self.rods = XRods()
        self.belt = (XBelt()
                     .rotate(90, [1, 0, 0])
                     .translate([0,
                                 XPlatform_width / 2 + XEnd_extra_width
                                 - belt_offset + thickness,
                                 0]))
        super().__init__(*args, **kwargs)

    def render(self):
        return [self.end_motor, self.end_idler, self.carriage,
                self.plate, self.rods, self.belt]
