"""The lasercut extruder."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bearing_608zz import Bearing608zz
from metamaquina2.hardware.bolt import Bolt
from metamaquina2.hardware.m8_locknut import M8Locknut
from metamaquina2.hardware.nema17_mount import Nema17Mount
from metamaquina2.params import (
    extruder_gear_angle,
    extruder_slice_height,
    extruder_washer_thickness,
    filament_channel_width,
    filament_channel_x,
    hobbed_bolt_position,
    jhead_bolt_positions,
    m3_diameter,
    motor_angle,
    motor_position,
    thickness,
)
from metamaquina2.x_stage.carriage.extruder.block import ExtruderBlock
from metamaquina2.x_stage.carriage.extruder.handle import POSITION, Handle
from metamaquina2.x_stage.carriage.extruder.hobbed_bolt import HobbedBolt
from metamaquina2.x_stage.carriage.extruder.hotend.hot_end import HotEnd
from metamaquina2.x_stage.carriage.extruder.idler.idler import Idler
from metamaquina2.x_stage.carriage.extruder.large_gear import ExtruderGear
from metamaquina2.x_stage.carriage.extruder.small_gear import MotorGear


#: Where the filament goes in, in this assembly's own frame.
#:
#: The middle slice is cut with a channel for it, and the mouth is
#: where that channel opens: on the channel's own axis, in the middle
#: slice, at the top face of a plain slice.  The cut itself is drawn
#: 70 long, which is an over-run past the profile rather than a height.
#:
#: The x is the design's, and it is not nought: `extruder_slice()` cuts
#: the channel, the two M3 holes that hold the hot end and the
#: nozzle-holder slot all three tenths of a millimetre to one side,
#: while the hot end below is drawn on the axis itself.  The two
#: disagree, the strand follows the channel, and a contract asks for
#: the difference so it cannot quietly go away.
FILAMENT_ENTRY = [filament_channel_x + filament_channel_width / 2, 0,
                  extruder_slice_height]


class Extruder(AssemblyNode):
    """A geared Wade extruder, cut from sheet instead of printed.

    The stepper drives the small gear, the small gear drives the big
    one, the big one turns the hobbed bolt, and the hobbed bolt drags
    filament past the idler and down into the hot end.  Two 608
    bearings carry the hobbed bolt in the block.

    Drawn standing on the carriage plate, facing along -Y; the
    carriage turns it to face the front of the machine.

    The hot end hangs under the block, held by two M3x30 through the
    holes the slices are cut with for them.  It is turned back out of
    the extruder's own frame, because the design draws it square with
    the machine rather than with the extruder: which way its heater
    block faces is set by the last quarter turn of tightening the
    nozzle, so it is free, and the design's choice is kept.
    """

    hobbed_bolt_drop = 30

    #: How long the bolts that hold the hot end are.  Two M3x30, bought
    #: by `extruder_block()` under `//TODO: Add these parts to the CAD
    #: model` and commented "for attaching the jhead_body", which is
    #: exactly what they are here.  Thirty is the five slices' own
    #: thickness, so each one just spans the block.
    hot_end_bolt = 30

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
                       .translate(POSITION))

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

        self.hot_end = HotEnd().rotate(-90, [0, 0, 1])
        self.hot_end_bolts = [
            Bolt(m3_diameter, self.hot_end_bolt)
            .rotate(-90, [1, 0, 0])
            .translate([x, 5 * thickness / 2, z])
            for x, z in jhead_bolt_positions
        ]

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
                + [self.motor, self.motor_gear, self.hot_end]
                + self.hot_end_bolts)
