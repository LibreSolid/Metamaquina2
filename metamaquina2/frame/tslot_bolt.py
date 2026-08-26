"""The bolt, washer and nut that close one t-slot joint."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bolt import Bolt
from metamaquina2.hardware.m3_nut import M3Nut
from metamaquina2.hardware.m3_washer import M3Washer
from metamaquina2.params import m3_washer_thickness, thickness


class TSlotBolt(AssemblyNode):
    """One t-slot fastener: an M3 bolt through the slot into a captive
    nut in the mating sheet's edge.

    The design draws these from a table of slot positions, in the plane
    of the sheet being bolted; this is one entry of that table.  Its
    origin is the middle of the slot, and the bolt runs down -Z into
    the sheet below.

    `flipped` bolts the joint from the other face.  The design does
    that with `mirror([0, 0, 1])` around the whole group; node
    operations have no mirror, but every part here is a solid of
    revolution about the bolt axis, so flipping each part end for end
    and negating its offset is the same geometry.
    """

    def __init__(self, length=16, flipped=False, **kwargs):
        self.length = length
        self.flipped = flipped

        def place(node, z):
            if flipped:
                node.rotate(180, [1, 0, 0])
                z = -z
            return node.translate([0, 0, z])

        self.washer = place(M3Washer(), thickness)
        self.bolt = place(Bolt(3, length), thickness + m3_washer_thickness)
        self.nut = place(M3Nut(), 8 - length)

        super().__init__(length, flipped, **kwargs)

    def render(self):
        return [self.washer, self.bolt, self.nut]
