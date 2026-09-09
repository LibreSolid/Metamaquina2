"""The belt side of the motor X end: its plate, the X motor and its
pulley."""

from solid_node.motion.joints import Revolute
from solid_node.motion.ports import RotationalPort
from solid_node.node import AssemblyNode

from metamaquina2.hardware.gt2_pulley import WIDTH, GT2Pulley
from metamaquina2.hardware.nema17_mount import Nema17Mount
from metamaquina2.params import (
    XEnd_box_size,
    XMotor_height,
    belt_offset,
    belt_width,
    thickness,
)
from metamaquina2.x_stage.ends.motor.belt_plate import XEndMotorBeltPlate
from metamaquina2.x_stage.x_belt import PERIOD


#: How far down the shaft the pulley sits, from the face of the plate
#: the motor is bolted through.
#:
#: The design says one `thickness`, which puts it hard against that
#: plate -- and 6 mm clear of the plane its own belt runs in.  Nothing
#: could show while `GT2_pulley` drew nothing to be 6 mm out of place.
#: So the depth is derived from the belt instead: this plate stands
#: half a thickness proud of the box, the belt runs `belt_offset` in
#: from the same face and one thickness back, and the difference
#: between those is where the belt is.  A pulley is where its belt is.
#:
#: Where the belt is, and centred on it: the bought pulley is 6 mm wide
#: and the design's belt 5, so the metal starts half a millimetre
#: before the rubber and ends half a millimetre after it.
PULLEY_DEPTH = belt_offset - 1.5 * thickness - (WIDTH - belt_width) / 2


class XPulley(GT2Pulley):
    """The pulley on the X motor shaft: a `GT2Pulley` that turns on the
    shaft the belt side bolts its motor to.

    The anchor's along-axis component is nought rather than
    `PULLEY_DEPTH`: the difference between the two points lies along
    the rotation axis, where the two centring translations a turn away
    from its own placed origin cancel it exactly, so the composed
    matrix is the same either way and `PULLEY_DEPTH` stays where
    `render()` needs it.
    """

    spin = Revolute(axis=(0, 0, 1),
                    at=(XEnd_box_size / 2, XMotor_height, 0.0),
                    unit='deg')


class XEndMotorBeltSide(AssemblyNode):
    """The plate, the motor bolted to it, and the pulley on its shaft,
    in the plate's own plane.

    `shaft` is which way that pulley faces.  It comes in from outside
    because nothing here knows: a pulley's phase is a fact about the
    belt meshed on it, and the belt is drawn from where the carriage
    stands, two assemblies up.  The wiring below carries it straight
    into the pulley's own turn.

    Nothing in this end travels except the pulley, so `render` stands
    the plate and the motor and the wiring is all there is to say per
    instant.
    """

    shaft = RotationalPort(unit='deg')

    plate = XEndMotorBeltPlate()
    motor = Nema17Mount()
    pulley = XPulley(period=PERIOD, spin=shaft)

    def render(self):
        """Stand the plate, bolt the motor to it, and put the pulley on
        the shaft.

        The pulley is drawn from nought to its own width along its
        axis, as the belt's section is along its own, so
        `PULLEY_DEPTH` alone lands the two in one plane.
        """
        self.plate.translate([0, thickness, 0])

        (self.motor
         .rotate(-180, [1, 0, 0])
         .translate([XEnd_box_size / 2, XMotor_height, 0]))

        self.pulley.translate(
            [XEnd_box_size / 2, XMotor_height, PULLEY_DEPTH])
