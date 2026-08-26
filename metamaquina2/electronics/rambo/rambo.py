"""The RAMBo controller, mounted on the left panel."""

from solid_node.node import AssemblyNode

from metamaquina2.electronics.rambo.cover import RamboCover
from metamaquina2.electronics.rambo.cover_bolt import CoverBolt
from metamaquina2.electronics.rambo.pcb import RamboPcb
from metamaquina2.electronics.rambo.psu_connector import PsuConnector
from metamaquina2.hardware.double_m3_spacer import DoubleM3Spacer
from metamaquina2.hardware.hexspacer_32mm import HexSpacer32mm
from metamaquina2.params import (
    RAMBo_border,
    RAMBo_cover_thickness,
    RAMBo_height,
    RAMBo_pcb_thickness,
    RAMBo_width,
    hexspacer_length,
    thickness,
)


class Rambo(AssemblyNode):
    """Board, cover, and the stack of spacers between them and the panel.

    At each of the four corners: two lasercut spacers hold the board
    off the panel, a hex spacer holds the cover off the board, and a
    bolt closes the stack.  Drawn in the left panel's own plane.
    """

    connector_position = (100, 60)

    def __init__(self, *args, **kwargs):
        corners = [
            (x, y)
            for x in (RAMBo_border, RAMBo_width - RAMBo_border)
            for y in (RAMBo_border, RAMBo_height - RAMBo_border)
        ]
        board_deck = 2 * thickness
        cover_deck = board_deck + RAMBo_pcb_thickness

        self.panel_spacers = [
            DoubleM3Spacer().translate([x, y, 0]) for x, y in corners
        ]
        self.cover_spacers = [
            HexSpacer32mm().translate([x, y, cover_deck]) for x, y in corners
        ]
        self.cover_bolts = [
            CoverBolt().translate(
                [x, y, cover_deck + hexspacer_length + RAMBo_cover_thickness])
            for x, y in corners
        ]

        self.board = RamboPcb().translate([0, 0, board_deck])
        self.connector = PsuConnector().translate(
            [self.connector_position[0], self.connector_position[1],
             cover_deck])
        self.cover = RamboCover().translate(
            [0, 0, cover_deck + hexspacer_length])

        super().__init__(*args, **kwargs)

    def render(self):
        return (self.panel_spacers + self.cover_spacers + self.cover_bolts
                + [self.board, self.connector, self.cover])
