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

    Each of the four is a different part -- the two limits use
    different spacer profiles -- so each is its own declaration, named
    by the string its class takes.
    """

    # where the Y switches sit in the bottom panel's plane
    y_max_position = (22.5, -24)
    y_min_position = (-22.5, 24)

    z_max = ZEndstop('max')
    z_min = ZEndstop('min')
    y_max = YEndstop('max')
    y_min = YEndstop('min')

    def render(self):
        frames.left_panel(
            self.z_max
            .rotate(180, [0, 0, 1])
            .translate([0, -2.5, 0])
            .translate([z_max_endstop_x, z_max_endstop_y, thickness]))
        frames.left_panel(
            self.z_min.translate(
                [z_min_endstop_x, z_min_endstop_y, thickness]))

        frames.bottom_panel(
            self.y_max.translate(
                [self.y_max_position[0], self.y_max_position[1], thickness]))
        frames.bottom_panel(
            self.y_min
            .rotate(180, [0, 0, 1])
            .translate(
                [self.y_min_position[0], self.y_min_position[1], thickness]))
