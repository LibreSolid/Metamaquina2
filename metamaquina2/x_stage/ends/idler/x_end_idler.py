"""The idler-side X end."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.tslot_bolt import TSlotBolt
from metamaquina2.hardware.lm8uu import LM8UU
from metamaquina2.hardware.m8_nut import M8Nut
from metamaquina2.params import (
    XEndIdler_back_face_TSLOTS,
    XEnd_box_size,
    XEnd_extra_width,
    XIdler_height,
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
from metamaquina2.x_stage.ends.idler.back_plate import XEndIdlerBackPlate
from metamaquina2.x_stage.ends.idler.belt_plate import XEndIdlerBeltPlate
from metamaquina2.x_stage.ends.idler.idler_pulley import XIdlerPulley
from metamaquina2.x_stage.ends.idler.plain_plate import XEndIdlerPlainPlate
from metamaquina2.x_stage.ends.zlink import ZLink
from metamaquina2.z_screw import NUT_SEAT


class XEndIdler(AssemblyNode):
    """The box at the right of the X beam.

    The same box as the motor end, turned around, with an idler
    bearing where the motor would be.  Its linear bearings are the
    motor end's mirrored: the design writes them with `mirror`, and a
    bearing is a cylinder about its own axis, so negating the offset
    is the same geometry.

    Its Z nut mirrors the same way and for a better reason than
    symmetry: the two bars turn together, so the two nuts have to be at
    the same height on them or the beam would rack.  Both are placed
    from `z_screw`, which is the one place that height is written down.
    """

    back_plate = XEndIdlerBackPlate()
    back_joints = TSlotBolt().repeat(len(XEndIdler_back_face_TSLOTS))
    bearing_sandwich = XEndBearingSandwich()
    front_plate = XEndFrontPlate()
    plain_plate = XEndIdlerPlainPlate()
    belt_plate = XEndIdlerBeltPlate()
    idler = XIdlerPulley()
    zlink = ZLink()
    nut = M8Nut()
    bearings = LM8UU().repeat(2)

    def render(self):
        def on_machine(node):
            return node.translate([machine_x_dim / 2, 0, 0])

        on_machine(
            self.back_plate
            .rotate(90, [0, 0, 1])
            .rotate(90, [0, 1, 0])
            .translate([-thickness, 0, 0]))
        for bolt, (x, y, width, angle) in zip(self.back_joints,
                                              XEndIdler_back_face_TSLOTS):
            on_machine(
                bolt
                .translate([0, width / 2, 0])
                .rotate(angle, [0, 0, 1])
                .translate([x, y, 0])
                .rotate(90, [0, 0, 1])
                .rotate(90, [0, 1, 0])
                .translate([-thickness, 0, 0]))

        on_machine(self.bearing_sandwich.rotate(180, [0, 0, 1]))

        on_machine(
            self.front_plate
            .rotate(-90, [0, 0, 1])
            .rotate(-90, [0, 1, 0])
            .translate([-XEnd_box_size - thickness, 0, 0]))

        on_machine(
            self.plain_plate
            .rotate(90, [1, 0, 0])
            .translate([-thickness - XEnd_box_size,
                        -XPlatform_width / 2 + 1.5 * thickness,
                        thickness]))

        on_machine(
            self.belt_plate
            .rotate(90, [1, 0, 0])
            .translate([-thickness - XEnd_box_size,
                        XPlatform_width / 2 + XEnd_extra_width
                        - 0.5 * thickness,
                        thickness]))

        on_machine(
            self.idler
            .rotate(90, [1, 0, 0])
            .translate([-XEnd_box_size / 2 - thickness,
                        XPlatform_width / 2 + XEnd_extra_width
                        - 2.5 * thickness,
                        XIdler_height]))

        on_machine(
            self.zlink
            .rotate(-90, [1, 0, 0])
            .rotate(-90, [0, 0, 1])
            .translate([-thickness - lm8uu_diameter / 2 - z_rod_z_bar_distance
                        - ZLink_rod_height,
                        0,
                        thickness + Zlink_hole_height]))

        on_machine(
            self.nut.translate(
                [-(thickness + lm8uu_diameter / 2 + z_rod_z_bar_distance),
                 0, NUT_SEAT]))

        for bearing, end in zip(self.bearings, (-1, 1)):
            on_machine(
                bearing
                .rotate(90, [1, 0, 0])
                .translate([-(thickness + lm8uu_diameter / 2), 0,
                            XPlatform_height / 2
                            + end * XPlatform_height / 2]))
