"""The spool holder, standing beside the machine."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.tslot_bolt import TSlotBolt
from metamaquina2.hardware.m8_domed_cap_nut import M8DomedCapNut
from metamaquina2.params import (
    SpoolHolder_TSLOTS,
    SpoolHolder_adjust,
    SpoolHolder_bar_diameter,
    SpoolHolder_bar_length,
    SpoolHolder_cap_nut_hole,
    SpoolHolder_top_cut_height,
    SpoolHolder_top_cut_width,
    SpoolHolder_total_height,
    SpoolHolder_total_width,
    SpoolHolder_width,
    thickness,
)
from metamaquina2.spool_holder.bar import SpoolHolderBar
from metamaquina2.spool_holder.end_panel import SpoolHolderEndPanel
from metamaquina2.spool_holder.side_panel import SpoolHolderSidePanel
from metamaquina2.spool_holder.spool import FilamentSpool


class SpoolHolder(AssemblyNode):
    """Two uprights, two end panels, a bar and the spool on it.

    A separate stand rather than part of the printer: it sits beside
    the machine and feeds filament up to the extruder, which is why the
    design draws it off to one side.
    """

    def __init__(self, *args, **kwargs):
        bar_height = (SpoolHolder_total_height - SpoolHolder_top_cut_height
                      - (SpoolHolder_top_cut_width
                         - SpoolHolder_bar_diameter) / 2)

        def upright(node, offset, turned):
            node.rotate(90, [1, 0, 0])
            if turned:
                node.rotate(180, [0, 0, 1])
            return node.translate([0, offset, 0]).rotate(90, [0, 0, 1])

        inset = SpoolHolder_width / 2 - thickness
        self.sides = [upright(SpoolHolderSidePanel(), -inset, False),
                      upright(SpoolHolderSidePanel(), inset, True)]
        self.side_joints = [
            upright(
                TSlotBolt()
                .translate([0, width / 2, 0])
                .rotate(angle, [0, 0, 1])
                .translate([x, y, 0]),
                -inset if side == 0 else inset,
                side == 1)
            for side in (0, 1)
            for x, y, width, angle in SpoolHolder_TSLOTS
        ]

        span = (SpoolHolder_total_width / 2 - thickness / 2
                - SpoolHolder_adjust / 2)
        self.ends = [
            SpoolHolderEndPanel()
            .rotate(90, [1, 0, 0])
            .translate([0, -span, 0]),
            SpoolHolderEndPanel()
            .rotate(90, [1, 0, 0])
            .rotate(180, [0, 0, 1])
            .translate([0, span, 0]),
        ]

        self.bar = (SpoolHolderBar()
                    .rotate(90, [0, 1, 0])
                    .translate([-SpoolHolder_bar_length / 2, 0, bar_height]))

        cap_offset = (SpoolHolder_bar_length
                      - 2 * SpoolHolder_cap_nut_hole) / 2
        self.cap_nuts = [
            M8DomedCapNut()
            .rotate(90, [0, 1, 0])
            .translate([cap_offset, 0, bar_height]),
            M8DomedCapNut()
            .rotate(270, [0, 1, 0])
            .translate([-cap_offset, 0, bar_height]),
        ]

        spool_height = (SpoolHolder_total_height - SpoolHolder_top_cut_height
                        - 35 / 2 + SpoolHolder_bar_diameter / 2
                        - (SpoolHolder_top_cut_width
                           - SpoolHolder_bar_diameter) / 2)
        self.spool = (FilamentSpool()
                      .rotate(90, [0, 1, 0])
                      .translate([-FilamentSpool.width / 2, 0, spool_height]))

        super().__init__(*args, **kwargs)

    def render(self):
        return (self.sides + self.side_joints + self.ends
                + [self.bar] + self.cap_nuts + [self.spool])
