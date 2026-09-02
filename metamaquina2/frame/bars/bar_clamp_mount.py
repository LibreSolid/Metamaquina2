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

    near_washer = M8Washer()
    near_nut = M8Nut()
    far_washer = M8Washer()
    far_nut = M8Nut()
    clamp = BarClamp()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def place(node, offset, forward):
            node.translate([0, 0, barclamp_thickness / 2 + offset])
            if not forward:
                node.rotate(180, [0, 1, 0])
            node.rotate(90, [0, 1, 0])

        place(self.near_washer, 0, True)
        place(self.near_nut, washer_thickness, True)
        place(self.far_washer, 0, False)
        place(self.far_nut, washer_thickness, False)

        (self.clamp
         .rotate(90, [1, 0, 0])
         .translate([-17, 6.7, -barclamp_thickness / 2])
         .rotate(90, [0, 1, 0]))
