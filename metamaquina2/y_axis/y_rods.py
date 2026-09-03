"""The pair of smooth rods the Y platform slides on."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.smooth_rod import SmoothRod
from metamaquina2.params import Y_rod_height, Y_rod_length, Y_rods_distance


class YRods(AssemblyNode):
    """Two 8 mm rods running front to back, held by the bar clamps."""

    rods = SmoothRod(length=Y_rod_length).repeat(2)

    def render(self):
        for rod, side in zip(self.rods, (-1, 1)):
            (rod
             .rotate(-90, [1, 0, 0])
             .translate([side * Y_rods_distance / 2,
                         -Y_rod_length / 2, Y_rod_height]))
