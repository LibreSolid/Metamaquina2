"""A printed bar clamp and the nuts that hold it on the bar."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.bars.barclamp import BarClamp
from metamaquina2.hardware.m8_nut import M8Nut
from metamaquina2.hardware.m8_washer import M8Washer
from metamaquina2.params import barclamp_thickness, washer_thickness


class BarClampMount(AssemblyNode):
    """One Y rod end: the clamp, locked between a nut on each side.

    The origin is the middle of the clamp and the threaded bar runs
    along X.
    """

    def __init__(self, *args, **kwargs):
        def place(node, offset, forward):
            node.translate([0, 0, barclamp_thickness / 2 + offset])
            if not forward:
                node.rotate(180, [0, 1, 0])
            return node.rotate(90, [0, 1, 0])

        self.near_washer = place(M8Washer(), 0, True)
        self.near_nut = place(M8Nut(), washer_thickness, True)
        self.far_washer = place(M8Washer(), 0, False)
        self.far_nut = place(M8Nut(), washer_thickness, False)

        self.clamp = (BarClamp()
                      .rotate(90, [1, 0, 0])
                      .translate([-17, 6.7, -barclamp_thickness / 2])
                      .rotate(90, [0, 1, 0]))

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.near_washer, self.near_nut,
                self.far_washer, self.far_nut, self.clamp]
