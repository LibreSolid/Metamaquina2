"""The pair of smooth rods the X carriage slides on."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.smooth_rod import SmoothRod
from metamaquina2.params import (
    X_rod_height,
    X_rod_length,
    X_rods_distance,
    thickness,
)


class XRods(AssemblyNode):
    """Two 8 mm rods running left to right between the X ends."""

    rods = SmoothRod(length=X_rod_length).repeat(2)

    def render(self):
        for rod, side in zip(self.rods, (-1, 1)):
            (rod
             .translate([0, 0, -X_rod_length / 2])
             .rotate(90, [0, 1, 0])
             .translate([0, side * X_rods_distance / 2,
                         thickness + X_rod_height]))
