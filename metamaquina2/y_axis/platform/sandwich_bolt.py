"""The washer and bolt that pull a bearing sandwich together."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bolt import Bolt
from metamaquina2.hardware.m3_washer import M3Washer
from metamaquina2.params import m3_washer_thickness


class SandwichBolt(AssemblyNode):
    """One M3x30 through the platform, its spacers and its sandwich
    plate, with a washer under the head.

    Drawn head-up from the origin; the platform turns it over to drive
    it downwards.
    """

    length = 30

    def __init__(self, *args, **kwargs):
        self.washer = M3Washer()
        self.bolt = Bolt(3, self.length).translate([0, 0, m3_washer_thickness])
        super().__init__(*args, **kwargs)

    def render(self):
        return [self.washer, self.bolt]
