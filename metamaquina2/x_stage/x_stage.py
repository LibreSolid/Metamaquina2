"""The X stage: the whole beam the Z axis lifts."""

from solid_node.node import AssemblyNode, TranslationalPort

from metamaquina2.params import (
    XCarPosition,
    XEnd_extra_width,
    XPlatform_width,
    belt_offset,
    thickness,
)
from metamaquina2.x_stage.carriage.x_carriage import XCarriage
from metamaquina2.x_stage.ends.idler.x_end_idler import XEndIdler
from metamaquina2.x_stage.ends.motor.x_end_motor import XEndMotor
from metamaquina2.x_stage.platform_plate import XPlatformPlate
from metamaquina2.x_stage.x_belt import CLAMP_ORIGIN, XBelt
from metamaquina2.x_stage.x_rods import XRods


class XStage(AssemblyNode):
    """The X beam and everything on it.

    A box at each end riding the Z rods, two smooth rods between them,
    a carriage on those rods, and a belt from the motor at one end to
    the idler at the other.  The whole assembly goes up and down as one
    thing, which is why it is one assembly.

    Where the carriage sits along the beam comes in through
    `carriage_position`, in the same X coordinate the design uses, and
    the machine is what wires it: the beam does not decide where its
    own carriage is any more than it decides its own height.  So this
    assembly no longer builds on its own -- an unconnected port has no
    value, and asking for one says so instead of quietly drawing the
    carriage at nought.

    Only the carriage moves.  The rods it slides on, the plate under
    them, the boxes at both ends and the loop the belt makes are all
    fixed in this frame.  The belt is the one part that is neither: its
    loop stands still while the teeth inside it travel with the
    carriage, so it takes the carriage's position too and re-draws
    itself from it rather than being placed.
    """

    carriage_position = TranslationalPort(unit='mm')

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
        """Slide the carriage to where the machine put it, and tell the
        belt where it is being held.

        The carriage is drawn at `XCarPosition`, the design's own rest
        knob, so what the beam applies here is the offset from rest and
        not the position itself.

        The belt is told the same position differently, because it is a
        length of belt rather than a place: the anchor is measured from
        where the upper run leaves the motor pulley, and the port's own
        scale turns millimetres along the beam into millimetres of belt
        across that slightly tilted run.
        """
        self.carriage.translate(
            [self.carriage_position.value - XCarPosition, 0, 0])

        self.connect(self.carriage_position.value - CLAMP_ORIGIN,
                     self.belt.clamp)

        return [self.end_motor, self.end_idler, self.carriage,
                self.plate, self.rods, self.belt]
