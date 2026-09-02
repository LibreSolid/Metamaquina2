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

    outer_washer = M8Washer()
    cap_nut = M8DomedCapNut()
    inner_washer = M8Washer()
    inner_nut = M8Nut()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def place(node, offset, outward):
            node.translate([0, 0, thickness / 2 + offset])
            if not outward:
                node.rotate(180, [0, 1, 0])
            (node
             .translate([0, 0, -thickness / 2])
             .rotate(90, [0, 1, 0]))

        place(self.outer_washer, 0, True)
        place(self.cap_nut, washer_thickness, True)
        place(self.inner_washer, 0, False)
        place(self.inner_nut, washer_thickness, False)
