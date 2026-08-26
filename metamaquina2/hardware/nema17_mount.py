"""A NEMA 17 bolted to a sheet: the motor and its four bolts."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bolt import Bolt
from metamaquina2.hardware.m3_washer import M3Washer
from metamaquina2.hardware.nema17 import Nema17
from metamaquina2.params import m3_washer_thickness, thickness


class Nema17Mount(AssemblyNode):
    """The design's `NEMA17_subassembly`, taken apart into its parts.

    A motor and eight fasteners, not one solid: the bolts come out.
    The bolt circle is the module's own default -- 15.5 mm from the
    shaft in both directions, through stock one `thickness` thick.
    """

    hole_distance = 15.5

    def __init__(self, *args, **kwargs):
        self.motor = Nema17()

        offset = -thickness - m3_washer_thickness
        self.washers = []
        self.bolts = []
        for x in (-self.hole_distance, self.hole_distance):
            for y in (-self.hole_distance, self.hole_distance):
                self.washers.append(
                    M3Washer().translate([x, y, offset]))
                self.bolts.append(
                    Bolt(3, 10)
                    .rotate(180, [1, 0, 0])
                    .translate([x, y, offset]))

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.motor] + self.washers + self.bolts
