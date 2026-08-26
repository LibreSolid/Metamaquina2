"""The lasercut extruder."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bearing_608zz import Bearing608zz
from metamaquina2.hardware.m8_locknut import M8Locknut
from metamaquina2.hardware.nema17_mount import Nema17Mount
from metamaquina2.params import (
    extruder_gear_angle,
    extruder_washer_thickness,
    hobbed_bolt_position,
    motor_angle,
    motor_position,
    thickness,
)
from metamaquina2.x_stage.carriage.extruder.block import ExtruderBlock
from metamaquina2.x_stage.carriage.extruder.handle import Handle
from metamaquina2.x_stage.carriage.extruder.hobbed_bolt import HobbedBolt
from metamaquina2.x_stage.carriage.extruder.idler.idler import Idler
from metamaquina2.x_stage.carriage.extruder.large_gear import ExtruderGear
from metamaquina2.x_stage.carriage.extruder.small_gear import MotorGear


class Extruder(AssemblyNode):
    """A geared Wade extruder, cut from sheet instead of printed.

    The stepper drives the small gear, the small gear drives the big
    one, the big one turns the hobbed bolt, and the hobbed bolt drags
    filament past the idler and down into the hot end.  Two 608
    bearings carry the hobbed bolt in the block.

    Drawn standing on the carriage plate, facing along -Y; the
    carriage turns it to face the front of the machine.
    """

    hobbed_bolt_drop = 30

    def __init__(self, *args, **kwargs):
        bolt_x, bolt_z = hobbed_bolt_position
        motor_x, motor_z = motor_position
        gear_gap = 5 * thickness / 2 + 2 * extruder_washer_thickness

        def upright(node):
            return (node
                    .rotate(90, [1, 0, 0])
                    .translate([0, 2.5 * thickness, 0]))

        self.block = upright(ExtruderBlock())
        self.idler = upright(Idler())

        self.handle = (Handle()
                       .rotate(-90, [0, 0, 1])
                       .rotate(-90, [0, 1, 0])
                       .translate([7, 0, 58]))

        self.gear = (ExtruderGear()
                     .rotate(90, [1, 0, 0])
                     .rotate(extruder_gear_angle, [0, 1, 0])
                     .translate([bolt_x, -gear_gap, bolt_z]))

        self.hobbed_bolt = (HobbedBolt()
                            .rotate(180, [1, 0, 0])
                            .translate([0, -self.hobbed_bolt_drop, 0])
                            .translate([bolt_x, 0, bolt_z]))
        self.hobbed_bolt_nut = (
            M8Locknut()
            .rotate(-90, [1, 0, 0])
            .translate([0, 5 * thickness / 2 + extruder_washer_thickness, 0])
            .translate([bolt_x, 0, bolt_z]))

        self.bearings = [
            Bearing608zz()
            .rotate(90, [1, 0, 0])
            .translate([bolt_x, -3 * thickness / 2, bolt_z]),
            Bearing608zz()
            .rotate(90, [1, 0, 0])
            .translate([bolt_x, 3 * thickness / 2 + 7, bolt_z]),
        ]

        def on_motor(node):
            return (node
                    .rotate(motor_angle, [0, 0, 1])
                    .rotate(-90, [1, 0, 0])
                    .translate([motor_x, -thickness / 2, motor_z]))

        self.motor = on_motor(Nema17Mount())
        self.motor_gear = on_motor(
            MotorGear()
            .rotate(180, [1, 0, 0])
            .translate([0, 0,
                        -2 * thickness - 2 * extruder_washer_thickness]))

        super().__init__(*args, **kwargs)

    def render(self):
        return ([self.block, self.idler, self.handle, self.gear,
                 self.hobbed_bolt, self.hobbed_bolt_nut]
                + self.bearings
                + [self.motor, self.motor_gear])
