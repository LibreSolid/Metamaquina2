"""The bolt, washer and nut that close one t-slot joint."""

from solid_node.node import AssemblyNode, Flag, Length

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
    and negating its offset is the same geometry.  It selects nothing:
    the same three parts are there either way, turned over.
    """

    length = Length(16.0, min=0)
    flipped = Flag(False)

    washer = M3Washer()
    bolt = Bolt(diameter=3.0, length=length)
    nut = M3Nut()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def place(node, z):
            if self.flipped:
                node.rotate(180, [1, 0, 0])
                z = -z
            node.translate([0, 0, z])

        place(self.washer, thickness)
        place(self.bolt, thickness + m3_washer_thickness)
        place(self.nut, 8 - self.length)
