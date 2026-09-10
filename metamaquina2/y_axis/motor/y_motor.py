"""The Y motor on its holder."""

from solid_node.motion.joints import Revolute
from solid_node.motion.ports import RotationalPort
from solid_node.node import AssemblyNode

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


class YPulley(GT2Pulley):
    """The pulley on the Y motor shaft, standing in the belt's own
    plane rather than the motor's.

    `render()` stands this pulley with two rotations that carry its
    own +Z onto the machine's -X, which is the fact `YMotor`'s own
    docstring used to spend a paragraph explaining: its local x lands
    on the loop's x and its axis on the loop's width.  `spin` is
    stated in this body's OWN rest frame, so it reads the shaft
    direction after those two rotations rather than before them: the
    machine's -X, carried back through `render()`'s
    `rotate(90,[1,0,0]).rotate(-90,[0,0,1])`, lands on this body's own
    +Z.  No anchor is needed -- the pulley is bored through its own
    origin.
    """

    spin = Revolute(axis=(0, 0, 1), unit='deg')


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
    pulley once it is bent backwards over it.  The wiring below carries
    it straight into the pulley's own turn.

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

    holder = YMotorHolder()
    motor = Nema17Mount()
    pulley = YPulley(period=PERIOD, spin=shaft)

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
        """Stand the plate, bolt the motor into it, and put the pulley
        in the belt's own plane on the shaft.

        Nothing here goes anywhere: the holder is bolted to the rear
        bars, the motor to the holder, and the pulley is bored onto a
        shaft that does not travel.

        The pulley's two rotations are the belt's own placement, so its
        local x lands on the loop's x and its axis on the loop's width:
        a groove drawn on the part's +X is then a groove at nought
        degrees of the plane `y_belt` measures its angles in.  What
        turns it is the wiring, from the shaft.
        """
        self.mounted(self.holder)
        self.on_motor(self.motor)

        self.pulley.rotate(90, [1, 0, 0])
        self.pulley.rotate(-90, [0, 0, 1])
        self.pulley.translate([belt_width / 2 - self.pulley_offset,
                               SHAFT[0], SHAFT[1]])
