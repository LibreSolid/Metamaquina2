"""The X stage: the whole beam the Z axis lifts."""

from solid_node.motion.joints import Prismatic
from solid_node.node import AssemblyNode

from metamaquina2.params import (
    XCarPosition,
    XEnd_extra_width,
    XPlatform_width,
    belt_offset,
    thickness,
)
from metamaquina2.x_stage import x_belt
from metamaquina2.x_stage.carriage.x_carriage import (
    FILAMENT_ENTRY as ENTRY_ON_THE_CARRIAGE,
    TOP as TOP_ON_THE_CARRIAGE,
    XCarriage,
)
from metamaquina2.x_stage.ends.idler.x_end_idler import XEndIdler
from metamaquina2.x_stage.ends.motor.x_end_motor import XEndMotor
from metamaquina2.x_stage.platform_plate import XPlatformPlate
from metamaquina2.x_stage.x_belt import XBelt
from metamaquina2.x_stage.x_rods import XRods


#: How high this beam stands, in its own frame.
#:
#: The carriage's own top, and not a function of where the carriage is:
#: it travels along this beam, not up it.  So this is a number where
#: `filament_entry` is a function, and it is what the machine has to
#: carry the filament over once the beam is high enough that the frame
#: is no longer the tallest thing in the way.
TOP = TOP_ON_THE_CARRIAGE


def filament_entry(carriage_position):
    """Where the filament goes in, in this beam's frame.

    A function of where the carriage is, the way `pulley_angle` is:
    what the beam knows about the filament is that its far end is on
    the carriage, and the carriage is drawn from the rest position the
    design's own knob puts it at.

    Taken here rather than in the machine so the beam that carries the
    carriage is what says where its extruder's mouth stands, and the
    machine only adds its own lift.
    """
    return [ENTRY_ON_THE_CARRIAGE[0] + carriage_position - XCarPosition,
            ENTRY_ON_THE_CARRIAGE[1],
            ENTRY_ON_THE_CARRIAGE[2]]


class XStage(AssemblyNode):
    """The X beam and everything on it.

    A box at each end riding the Z rods, two smooth rods between them,
    a carriage on those rods, and a belt from the motor at one end to
    the idler at the other.  The whole assembly goes up and down as one
    thing, which is why it is one assembly.

    `lift` is how far this beam has climbed the Z rods, and the machine
    is what drives it.

    The carriage moves, and so does one other thing: the pulley the
    belt is meshed on turns.  Both come from the motor's own shaft, the
    two sentences below: the shaft is a fact about the belt, so it
    drives the belt's clamp and the carriage's own slide at once, and
    the wiring on the belt side carries it into the pulley's turn.  The
    rods the carriage slides on, the plate under them, the boxes at
    both ends and the loop the belt makes are all fixed in this frame.
    The belt is the one part that is neither placed nor still: its loop
    stands still while the teeth inside it travel with the carriage, so
    it takes the carriage's position too and re-draws itself from it
    rather than being placed.
    """

    lift = Prismatic(axis=(0, 0, 1), unit='mm')

    end_motor = XEndMotor()
    end_idler = XEndIdler()
    carriage = XCarriage()
    plate = XPlatformPlate()
    rods = XRods()
    belt = XBelt()

    #: The motor shaft's own angle drives the belt's clamp and the
    #: carriage's slide alike, at the pitch arc's rate.  `PULLEY_AT_ORIGIN`
    #: is the shaft's own angle with the clamp at nought, so each
    #: relation's offset is that phase read back through the rate to
    #: the coordinate it drives -- `CLAMP_ORIGIN` and `XCarPosition` the
    #: extra terms the carriage's own rest and the belt's own anchor
    #: differ by.
    end_motor.belt_side.shaft.drives(
        belt.clamp,
        ratio=-x_belt.BEAM_PER_DEGREE,
        offset=x_belt.PULLEY_AT_ORIGIN * x_belt.BEAM_PER_DEGREE)
    end_motor.belt_side.shaft.drives(
        carriage.travel,
        ratio=-x_belt.BEAM_PER_DEGREE,
        offset=(x_belt.PULLEY_AT_ORIGIN * x_belt.BEAM_PER_DEGREE
                + x_belt.CLAMP_ORIGIN - XCarPosition))

    def render(self):
        """Stand the belt loop where its idlers and its pulley hold it.

        The loop does not go anywhere -- both its ends are bolted down
        -- so where it stands in this frame is said here.  What travels
        inside it is told to it every instant, as a port.
        """
        (self.belt
         .rotate(90, [1, 0, 0])
         .translate([0,
                     XPlatform_width / 2 + XEnd_extra_width
                     - belt_offset + thickness,
                     0]))
