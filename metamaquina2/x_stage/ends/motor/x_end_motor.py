"""The motor-side X end."""

from solid_node.motion.ports import RotationalPort
from solid_node.node import AssemblyNode

from metamaquina2.frame.tslot_bolt import TSlotBolt
from metamaquina2.hardware.lm8uu import LM8UU
from metamaquina2.hardware.m8_nut import M8Nut
from metamaquina2.params import (
    XEndMotor_back_face_TSLOTS,
    XEnd_box_size,
    XEnd_extra_width,
    XPlatform_height,
    XPlatform_width,
    ZLink_rod_height,
    Zlink_hole_height,
    lm8uu_diameter,
    machine_x_dim,
    thickness,
    z_rod_z_bar_distance,
)
from metamaquina2.x_stage.ends.bearing_sandwich import XEndBearingSandwich
from metamaquina2.x_stage.ends.front_plate import XEndFrontPlate
from metamaquina2.x_stage.ends.motor.back_plate import XEndMotorBackPlate
from metamaquina2.x_stage.ends.motor.belt_side import XEndMotorBeltSide
from metamaquina2.x_stage.ends.motor.plain_plate import XEndMotorPlainPlate
from metamaquina2.x_stage.ends.zlink import ZLink
from metamaquina2.z_screw import NUT_SEAT


class XEndMotor(AssemblyNode):
    """The box at the left of the X beam.

    Five plates bolted into a box, two Z bearings clamped inside it by
    the sandwich, a Z link on the outside with the M8 nut that carries
    this end of the beam captive in it, and the X motor and its pulley
    on the belt side.  The whole thing sits at the far left of the
    machine.

    The nut is the load path and is placed as one: it stands on the Z
    bar's own axis with its top face against the Z link's captive
    plate, which is what the weight of the beam comes down on.  Where
    that is, `z_screw` says, because the machine has to turn the bars
    to the phase that puts a thread under it.

    `shaft` passes straight through to the belt side, which is where
    the pulley is.  The box has nothing to say about the angle -- it is
    a fact about the belt, which the beam above owns -- so it relays it
    rather than deriving anything from it.
    """

    shaft = RotationalPort(unit='deg')

    back_plate = XEndMotorBackPlate()
    back_joints = TSlotBolt().repeat(len(XEndMotor_back_face_TSLOTS))
    bearing_sandwich = XEndBearingSandwich()
    front_plate = XEndFrontPlate()
    plain_plate = XEndMotorPlainPlate()
    belt_side = XEndMotorBeltSide()
    zlink = ZLink()
    nut = M8Nut()
    bearings = LM8UU().repeat(2)

    def render(self):
        def on_machine(node):
            return node.translate([-machine_x_dim / 2, 0, 0])

        def upright(node, offset):
            """Stand a plate across the beam, facing along it."""
            return (node
                    .rotate(-90, [0, 0, 1])
                    .rotate(-90, [0, 1, 0])
                    .translate([offset, 0, 0]))

        on_machine(upright(self.back_plate, thickness))
        for bolt, (x, y, width, angle) in zip(self.back_joints,
                                              XEndMotor_back_face_TSLOTS):
            on_machine(upright(
                bolt
                .translate([0, width / 2, 0])
                .rotate(angle, [0, 0, 1])
                .translate([x, y, 0]), thickness))

        on_machine(self.bearing_sandwich)

        on_machine(upright(self.front_plate, XEnd_box_size + 2 * thickness))

        on_machine(
            self.plain_plate
            .rotate(90, [1, 0, 0])
            .translate([thickness,
                        -XPlatform_width / 2 + 1.5 * thickness,
                        thickness]))

        on_machine(
            self.belt_side
            .rotate(90, [1, 0, 0])
            .translate([thickness,
                        XPlatform_width / 2 + XEnd_extra_width
                        - 0.5 * thickness, 0]))

        on_machine(
            self.zlink
            .rotate(-90, [1, 0, 0])
            .rotate(90, [0, 0, 1])
            .translate([thickness + lm8uu_diameter / 2 + z_rod_z_bar_distance
                        + ZLink_rod_height,
                        0,
                        thickness + Zlink_hole_height]))

        on_machine(
            self.nut.translate(
                [thickness + lm8uu_diameter / 2 + z_rod_z_bar_distance,
                 0, NUT_SEAT]))

        for bearing, end in zip(self.bearings, (-1, 1)):
            on_machine(
                bearing
                .rotate(90, [1, 0, 0])
                .translate([thickness + lm8uu_diameter / 2, 0,
                            XPlatform_height / 2
                            + end * XPlatform_height / 2]))

    def simulate(self):
        """Hand the pulley's phase on to the box that holds it.

        Nothing in this box moves -- the beam carries the whole of it
        -- so `render` stands every plate, bolt and bearing, and the
        one wire is all there is to say per instant.
        """
        self.connect(self.shaft, self.belt_side.shaft)
