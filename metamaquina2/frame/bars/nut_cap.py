"""The pair of nuts that clamp a threaded bar through a side panel."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.m8_domed_cap_nut import M8DomedCapNut
from metamaquina2.hardware.m8_nut import M8Nut
from metamaquina2.hardware.m8_washer import M8Washer
from metamaquina2.params import thickness, washer_thickness


class NutCap(AssemblyNode):
    """Where a horizontal bar leaves the machine through a side panel.

    A nut and washer inside pull the panel against the bar; a washer
    and a domed cap nut outside finish the end so nothing sharp sticks
    out.  The origin is the middle of the panel and the bar runs along
    X.
    """

    def __init__(self, *args, **kwargs):
        def place(node, offset, outward):
            node.translate([0, 0, thickness / 2 + offset])
            if not outward:
                node.rotate(180, [0, 1, 0])
            return (node
                    .translate([0, 0, -thickness / 2])
                    .rotate(90, [0, 1, 0]))

        self.outer_washer = place(M8Washer(), 0, True)
        self.cap_nut = place(M8DomedCapNut(), washer_thickness, True)
        self.inner_washer = place(M8Washer(), 0, False)
        self.inner_nut = place(M8Nut(), washer_thickness, False)

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.outer_washer, self.cap_nut,
                self.inner_washer, self.inner_nut]
