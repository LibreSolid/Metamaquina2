"""A 608 bearing running as an idler on a horizontal frame bar."""

from solid_node.node import AssemblyNode, Flag

from metamaquina2.hardware.bearing_608zz import Bearing608zz
from metamaquina2.hardware.m8_mudguard_washer import M8MudguardWasher
from metamaquina2.hardware.m8_nut import M8Nut
from metamaquina2.hardware.m8_washer import M8Washer
from metamaquina2.params import (
    bearing_thickness,
    mudguard_washer_thickness,
    thickness,
    washer_thickness,
)


class BeltIdler(AssemblyNode):
    """One Y belt idler: a bearing on the bar, kept centred by a stack
    of washers and nuts on each side.

    The mudguard washers are what the belt actually runs against, so
    they are what keeps it from walking off the bearing.  `spaced`
    adds the extra washer the rear bars need to clear the panel behind
    them, and pushes the far nut out past it -- so the flag selects one
    part's presence and one nut's offset, which is exactly what a
    structural flag is for.  The origin is the middle of the bearing
    and the bar runs along X.
    """

    spaced = Flag(False)

    #: Two washers against the bearing, and the third the spacing needs.
    washers = M8Washer().repeat(3)
    mudguard_washers = M8MudguardWasher().repeat(2)
    nuts = M8Nut().repeat(2)
    bearing = Bearing608zz()

    def render(self):
        def place(node, offset, forward):
            node.translate([0, 0, bearing_thickness / 2 + offset])
            if not forward:
                node.rotate(180, [0, 1, 0])
            node.rotate(90, [0, 1, 0])

        place(self.washers[0], 0, True)
        place(self.washers[1], 0, False)
        place(self.mudguard_washers[0], washer_thickness, True)
        place(self.mudguard_washers[1], washer_thickness, False)

        offset = washer_thickness + mudguard_washer_thickness
        place(self.nuts[0], offset, True)
        if self.spaced:
            place(self.washers[2], offset + thickness, False)
            place(self.nuts[1],
                  offset + thickness + washer_thickness, False)
        else:
            self.washers[2].omit()
            place(self.nuts[1], offset, False)

        (self.bearing
         .translate([0, 0, -bearing_thickness / 2])
         .rotate(90, [0, 1, 0]))
