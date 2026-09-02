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

    Four washers and four bolts, each declared once and placed four
    times: they are the same part on every corner, so they are one
    line of the bill of materials and one artifact.
    """

    hole_distance = 15.5

    motor = Nema17()
    washers = M3Washer().repeat(4)
    bolts = Bolt(diameter=3, length=10).repeat(4)

    def holes(self):
        """The four corners of the bolt circle, in the motor's frame."""
        return [(x, y)
                for x in (-self.hole_distance, self.hole_distance)
                for y in (-self.hole_distance, self.hole_distance)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        offset = -thickness - m3_washer_thickness
        for corner, (x, y) in enumerate(self.holes()):
            self.washers[corner].translate([x, y, offset])
            (self.bolts[corner]
             .rotate(180, [1, 0, 0])
             .translate([x, y, offset]))
