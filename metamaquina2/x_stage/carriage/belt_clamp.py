"""An X belt clamp and the bolts that tighten it."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bolt import Bolt
from metamaquina2.hardware.m3_washer import M3Washer
from metamaquina2.params import m3_washer_thickness
from metamaquina2.x_stage.carriage.belt_clamp_plate import XBeltClampPlate


class XBeltClamp(AssemblyNode):
    """One clamp: a plate and two M3x20 through it into the carriage.

    `flipped` is the other end of the belt.  The design mirrors the
    clamp there, and a flat plate mirrored in its own plane is the same
    piece turned over -- so it is turned over, and lifted back by its
    own thickness so it still lies where it was.  The bolts are on the
    mirror line, so they are the same either way.
    """

    bolt_offset = 9
    bolt_length = 20

    def __init__(self, flipped=False, **kwargs):
        self.flipped = flipped

        plate = XBeltClampPlate()
        if flipped:
            plate.rotate(180, [1, 0, 0]).translate(
                [0, 0, XBeltClampPlate.clamp_thickness])
        self.plate = plate

        self.washers = []
        self.bolts = []
        for side in (-1, 1):
            self.washers.append(
                M3Washer()
                .translate([side * self.bolt_offset, 0, 0])
                .rotate(180, [1, 0, 0]))
            self.bolts.append(
                Bolt(3, self.bolt_length)
                .translate([0, 0, m3_washer_thickness])
                .translate([side * self.bolt_offset, 0, 0])
                .rotate(180, [1, 0, 0]))

        super().__init__(flipped, **kwargs)

    def render(self):
        return [self.plate] + self.washers + self.bolts
