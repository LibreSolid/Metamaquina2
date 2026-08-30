"""The Y motor on its holder."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.gt2_pulley import WIDTH, GT2Pulley
from metamaquina2.hardware.nema17_mount import Nema17Mount
from metamaquina2.params import (
    RightPanel_basewidth,
    bar_cut_length,
    feetheight,
)
from metamaquina2.y_axis.motor.motor_holder import YMotorHolder


class YMotor(AssemblyNode):
    """The Y stepper, its holder plate, its mounting bolts and the
    pulley on its shaft.

    The whole assembly hangs off the rear of the machine, turned on its
    side so the motor tucks in behind the rear bars, which is where the
    design puts it.

    The pulley does not turn, and that is a statement about the design
    rather than about this node.  The loop the design draws for this
    axis runs on three bare 608 bearings and never comes near the
    motor: the nearest of the three is thirty millimetres away from
    this shaft, with nothing drawn between them.  So there is nothing
    for these teeth to be meshed with, and an angle for them would be
    invented rather than derived -- it would claim a drive the geometry
    does not have.  The X pulley turns because its belt is wrapped
    round it and can be measured.
    """

    # where the holder plate meets the rear bars
    mount_height = 60 + feetheight + 12

    #: How far down the shaft the belt's plane falls, from the motor's
    #: own face.
    #:
    #: The design puts its `GT2_pulley()` at the origin of this
    #: assembly, which is on the holder plate and 72 mm off the shaft
    #: -- a placement nobody could see was wrong while the module drew
    #: nothing.  So it is derived instead, and there is exactly one
    #: place a pulley on this shaft can go: the mount stands the motor
    #: face 14 mm off the machine's centre plane measured along its own
    #: shaft -- the holder's 7 and the motor's 7 within it, both of
    #: which the mount turns onto the machine's X -- and the belt runs
    #: in a band `belt_width` wide centred on that plane.  The shaft is
    #: 24 mm long, so it reaches, with 7 mm to spare.
    #:
    #: This is that plane itself rather than an edge of the band, so
    #: the pulley can be hung on it by its own middle: it is 6 mm wide
    #: where the design's belt is 5.
    pulley_depth = 7 + 7

    def __init__(self, *args, **kwargs):
        def mounted(node):
            return (node
                    .rotate(180, [0, 0, 1])
                    .rotate(-90, [0, 1, 0])
                    .translate([-7,
                                RightPanel_basewidth / 2 - bar_cut_length,
                                self.mount_height]))

        def on_motor(node):
            """Put `node` in the motor's own frame, wherever the mount
            has swung that to."""
            return mounted(node
                           .rotate(180, [1, 0, 0])
                           .rotate(-135, [0, 0, 1])
                           .translate([40, -60, -7])
                           .rotate(180, [1, 0, 0]))

        self.holder = mounted(YMotorHolder())
        self.motor = on_motor(Nema17Mount())
        # The shaft runs down -Z from the motor's face, so a pulley
        # drawn from nought to its own width has to be sent the far
        # side of where it sits.
        self.pulley = on_motor(
            GT2Pulley().translate([0, 0, -self.pulley_depth - WIDTH / 2]))

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.holder, self.motor, self.pulley]
