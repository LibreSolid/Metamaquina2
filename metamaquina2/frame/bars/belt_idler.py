"""A 608 bearing running as an idler on a horizontal frame bar."""

from solid_node.node import AssemblyNode

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
    adds the extra washer and nut the rear bars need to clear the
    panel behind them.  The origin is the middle of the bearing and
    the bar runs along X.
    """

    def __init__(self, spaced=False, **kwargs):
        self.spaced = spaced

        def place(node, offset, forward):
            node.translate([0, 0, bearing_thickness / 2 + offset])
            if not forward:
                node.rotate(180, [0, 1, 0])
            return node.rotate(90, [0, 1, 0])

        self.washers = []
        self.mudguard_washers = []
        self.nuts = []
        for forward in (True, False):
            self.washers.append(place(M8Washer(), 0, forward))
            self.mudguard_washers.append(
                place(M8MudguardWasher(), washer_thickness, forward))

            offset = washer_thickness + mudguard_washer_thickness
            if spaced and not forward:
                self.washers.append(
                    place(M8Washer(), offset + thickness, forward))
                self.nuts.append(
                    place(M8Nut(), offset + thickness + washer_thickness,
                          forward))
            else:
                self.nuts.append(place(M8Nut(), offset, forward))

        self.bearing = (Bearing608zz()
                        .translate([0, 0, -bearing_thickness / 2])
                        .rotate(90, [0, 1, 0]))

        super().__init__(spaced, **kwargs)

    def render(self):
        return (self.washers + self.mudguard_washers + self.nuts
                + [self.bearing])
