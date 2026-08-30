"""The belt side of the motor X end: its plate, the X motor and its
pulley."""

from solid_node.node import AssemblyNode, RotationalPort

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


class XEndMotorBeltSide(AssemblyNode):
    """The plate, the motor bolted to it, and the pulley on its shaft,
    in the plate's own plane.

    `shaft` is which way that pulley faces.  It comes in from outside
    because nothing here knows: a pulley's phase is a fact about the
    belt meshed on it, and the belt is drawn from where the carriage
    stands, two assemblies up.  So this end no longer builds on its
    own, in the same way and for the same reason the beam above it does
    not -- an unconnected port has no value, and asking for one says so
    instead of quietly drawing a tooth through a tooth.

    The rotation is applied before the placement, so it turns the
    pulley about its own axis rather than swinging it around the
    plate's corner, and both are applied in `render` so that re-drawing
    at a new carriage position replaces them rather than piling onto
    them.
    """

    shaft = RotationalPort(unit='deg')

    def __init__(self, *args, **kwargs):
        self.plate = XEndMotorBeltPlate().translate([0, thickness, 0])
        self.motor = (Nema17Mount()
                      .rotate(-180, [1, 0, 0])
                      .translate([XEnd_box_size / 2, XMotor_height, 0]))
        self.pulley = GT2Pulley(period=PERIOD)
        super().__init__(*args, **kwargs)

    def render(self):
        """Turn the pulley to where the belt's teeth are, and put it on
        the shaft.

        Drawn from nought to its own width along its axis, as the belt's
        section is along its own, so `PULLEY_DEPTH` alone lands the two
        in one plane.
        """
        self.pulley.rotate(self.shaft.value, [0, 0, 1])
        self.pulley.translate(
            [XEnd_box_size / 2, XMotor_height, PULLEY_DEPTH])

        return [self.plate, self.motor, self.pulley]
