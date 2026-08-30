"""The Y motor on its holder."""

from solid_node.node import AssemblyNode, RotationalPort

from metamaquina2.hardware.gt2_pulley import WIDTH, GT2Pulley
from metamaquina2.hardware.nema17_mount import Nema17Mount
from metamaquina2.params import (
    RightPanel_basewidth,
    bar_cut_length,
    belt_width,
)
from metamaquina2.y_axis.motor.motor_holder import YMotorHolder
from metamaquina2.y_axis.motor.mount import ALONG, ACROSS, DEPTH, HEIGHT, SHAFT
from metamaquina2.y_axis.y_belt import PERIOD


class YMotor(AssemblyNode):
    """The Y stepper, its holder plate, its mounting bolts and the
    pulley on its shaft.

    The whole assembly hangs off the rear of the machine, turned on its
    side so the motor tucks in behind the rear bars, which is where the
    design puts it.

    `shaft` is which way the pulley faces, and it comes in from outside
    because nothing here knows: a pulley's phase is a fact about the
    belt meshed on it, and the belt is drawn from where the bed stands,
    one assembly up.  The design could not have asked the question --
    its `GT2_pulley` draws nothing and its belt runs three bare
    bearings and stops thirty millimetres short of this shaft -- but
    the machine it draws is driven from here, and the loop reaches the
    pulley once it is bent backwards over it.

    The pulley is placed from the belt rather than from the motor.  Its
    axis is the shaft's, which the mount fixes; where it stands along
    that axis, and which way round its own frame lies, are the belt's,
    because a groove has to meet a tooth in the belt's own plane and
    not in whatever frame a chain of mounting rotations happens to
    leave.  That the two agree -- that a pulley placed from the belt is
    still bored onto the shaft -- is a contract the tests hold.
    """

    shaft = RotationalPort(unit='deg')

    # where the holder plate meets the rear bars
    mount_height = HEIGHT

    #: How far along the shaft the pulley's near face stands, measured
    #: in the belt's own width direction.
    #:
    #: The belt runs in a band `belt_width` wide starting at nought, and
    #: the bought pulley is 6 mm where the design's belt is 5, so the
    #: metal starts half a millimetre before the rubber and ends half a
    #: millimetre after it.  The design put its `GT2_pulley()` at the
    #: origin of this assembly instead, 72 mm off the shaft -- a
    #: placement nobody could see was wrong while the module drew
    #: nothing.
    pulley_offset = -(WIDTH - belt_width) / 2

    def __init__(self, *args, **kwargs):
        self.holder = self.mounted(YMotorHolder())
        self.motor = self.on_motor(Nema17Mount())
        self.pulley = GT2Pulley(period=PERIOD)

        super().__init__(*args, **kwargs)

    def mounted(self, node):
        """Stand `node` in the holder's frame, behind the rear bar."""
        return (node
                .rotate(180, [0, 0, 1])
                .rotate(-90, [0, 1, 0])
                .translate([-DEPTH,
                            RightPanel_basewidth / 2 - bar_cut_length,
                            self.mount_height]))

    def on_motor(self, node):
        """Put `node` in the motor's own frame, wherever the mount has
        swung that to."""
        return self.mounted(node
                            .rotate(180, [1, 0, 0])
                            .rotate(-135, [0, 0, 1])
                            .translate([ACROSS, -ALONG, -DEPTH])
                            .rotate(180, [1, 0, 0]))

    def render(self):
        """Turn the pulley to where the belt's teeth are, and stand it
        in the belt's own plane on the shaft.

        The two rotations are the belt's own placement, so the pulley's
        local x lands on the loop's x and its axis on the loop's width:
        a groove drawn on the part's +X is then a groove at nought
        degrees of the plane `y_belt` measures its angles in.  The turn
        goes on before them, so it turns the pulley about its own axis
        rather than swinging it around the machine.
        """
        self.pulley.rotate(self.shaft.value, [0, 0, 1])
        self.pulley.rotate(90, [1, 0, 0])
        self.pulley.rotate(-90, [0, 0, 1])
        self.pulley.translate([belt_width / 2 - self.pulley_offset,
                               SHAFT[0], SHAFT[1]])

        return [self.holder, self.motor, self.pulley]
