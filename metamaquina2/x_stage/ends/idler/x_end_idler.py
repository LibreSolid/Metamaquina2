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

    def __init__(self, *args, **kwargs):
        def on_machine(node):
            return node.translate([machine_x_dim / 2, 0, 0])

        self.back_plate = on_machine(
            XEndIdlerBackPlate()
            .rotate(90, [0, 0, 1])
            .rotate(90, [0, 1, 0])
            .translate([-thickness, 0, 0]))
        self.back_joints = [
            on_machine(
                TSlotBolt()
                .translate([0, width / 2, 0])
                .rotate(angle, [0, 0, 1])
                .translate([x, y, 0])
                .rotate(90, [0, 0, 1])
                .rotate(90, [0, 1, 0])
                .translate([-thickness, 0, 0]))
            for x, y, width, angle in XEndIdler_back_face_TSLOTS
        ]

        self.bearing_sandwich = on_machine(
            XEndBearingSandwich().rotate(180, [0, 0, 1]))

        self.front_plate = on_machine(
            XEndFrontPlate()
            .rotate(-90, [0, 0, 1])
            .rotate(-90, [0, 1, 0])
            .translate([-XEnd_box_size - thickness, 0, 0]))

        self.plain_plate = on_machine(
            XEndIdlerPlainPlate()
            .rotate(90, [1, 0, 0])
            .translate([-thickness - XEnd_box_size,
                        -XPlatform_width / 2 + 1.5 * thickness,
                        thickness]))

        self.belt_plate = on_machine(
            XEndIdlerBeltPlate()
            .rotate(90, [1, 0, 0])
            .translate([-thickness - XEnd_box_size,
                        XPlatform_width / 2 + XEnd_extra_width
                        - 0.5 * thickness,
                        thickness]))

        self.idler = on_machine(
            XIdlerPulley()
            .rotate(90, [1, 0, 0])
            .translate([-XEnd_box_size / 2 - thickness,
                        XPlatform_width / 2 + XEnd_extra_width
                        - 2.5 * thickness,
                        XIdler_height]))

        self.zlink = on_machine(
            ZLink()
            .rotate(-90, [1, 0, 0])
            .rotate(-90, [0, 0, 1])
            .translate([-thickness - lm8uu_diameter / 2 - z_rod_z_bar_distance
                        - ZLink_rod_height,
                        0,
                        thickness + Zlink_hole_height]))

        self.nut = on_machine(
            M8Nut().translate(
                [-(thickness + lm8uu_diameter / 2 + z_rod_z_bar_distance),
                 0, NUT_SEAT]))

        self.bearings = [
            on_machine(
                LM8UU()
                .rotate(90, [1, 0, 0])
                .translate([-(thickness + lm8uu_diameter / 2), 0,
                            XPlatform_height / 2 + end * XPlatform_height / 2]))
            for end in (-1, 1)
        ]

        super().__init__(*args, **kwargs)

    def render(self):
        return ([self.back_plate] + self.back_joints
                + [self.bearing_sandwich, self.front_plate,
                   self.plain_plate, self.belt_plate, self.idler,
                   self.zlink, self.nut]
                + self.bearings)
