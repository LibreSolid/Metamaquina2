"""All four endstops, on the panels they mount to."""

from solid_node.node import AssemblyNode

from metamaquina2 import frames
from metamaquina2.electronics.endstops.y_endstop import YEndstop
from metamaquina2.electronics.endstops.z_endstop import ZEndstop
from metamaquina2.params import (
    thickness,
    z_max_endstop_x,
    z_max_endstop_y,
    z_min_endstop_x,
    z_min_endstop_y,
)


class Endstops(AssemblyNode):
    """Two on the left panel for Z, two on the bottom panel for Y.

    There is no X endstop assembly here: the design lists the X
    microswitches in the carriage's bill of materials but never draws
    them, so there is nothing to place.
    """

    # where the Y switches sit in the bottom panel's plane
    y_max_position = (22.5, -24)
    y_min_position = (-22.5, 24)

    def __init__(self, *args, **kwargs):
        self.z_max = frames.left_panel(
            ZEndstop('max')
            .rotate(180, [0, 0, 1])
            .translate([0, -2.5, 0])
            .translate([z_max_endstop_x, z_max_endstop_y, thickness]))
        self.z_min = frames.left_panel(
            ZEndstop('min')
            .translate([z_min_endstop_x, z_min_endstop_y, thickness]))

        self.y_max = frames.bottom_panel(
            YEndstop('max').translate(
                [self.y_max_position[0], self.y_max_position[1], thickness]))
        self.y_min = frames.bottom_panel(
            YEndstop('min')
            .rotate(180, [0, 0, 1])
            .translate(
                [self.y_min_position[0], self.y_min_position[1], thickness]))

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.z_max, self.z_min, self.y_max, self.y_min]
