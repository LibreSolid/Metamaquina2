"""The six plates that cap the Z rods and Z bars."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.panels.rod_ends.rod_end_bottom import RodEndBottom
from metamaquina2.frame.panels.rod_ends.rod_end_top import RodEndTop
from metamaquina2.frame.panels.rod_ends.secondary_rod_end_top import (
    SecondaryRodEndTop)
from metamaquina2.params import (
    BottomPanel_zoffset,
    XZStage_offset,
    Z_rods_distance,
    machine_height,
    thickness,
)


class RodEnds(AssemblyNode):
    """Both ends of both Z rods.

    Each top end is two plates -- one above the top panel and a shorter
    one below it -- clamping the panel between them; each bottom end is
    a single plate under the bottom panel.  The right-hand plates are
    the same parts as the left, turned around.
    """

    top_left = RodEndTop()
    top_left_secondary = SecondaryRodEndTop()
    top_right = RodEndTop()
    top_right_secondary = SecondaryRodEndTop()
    bottom_left = RodEndBottom()
    bottom_right = RodEndBottom()

    def render(self):
        left = -Z_rods_distance / 2
        right = Z_rods_distance / 2

        self.top_left.translate(
            [left, -XZStage_offset, machine_height + thickness])
        self.top_left_secondary.translate(
            [left, -XZStage_offset, machine_height - thickness])

        (self.top_right
         .rotate(180, [0, 0, 1])
         .translate([right, -XZStage_offset, machine_height + thickness]))
        (self.top_right_secondary
         .rotate(180, [0, 0, 1])
         .translate([right, -XZStage_offset, machine_height - thickness]))

        self.bottom_left.translate(
            [left, -XZStage_offset, BottomPanel_zoffset - thickness])
        (self.bottom_right
         .rotate(180, [0, 0, 1])
         .translate([right, -XZStage_offset,
                     BottomPanel_zoffset - thickness]))
