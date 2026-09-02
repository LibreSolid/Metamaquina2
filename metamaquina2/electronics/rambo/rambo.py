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


#: The four corners the board and its cover are stacked at, in the
#: board's own plane.
CORNERS = [
    (x, y)
    for x in (RAMBo_border, RAMBo_width - RAMBo_border)
    for y in (RAMBo_border, RAMBo_height - RAMBo_border)
]


class Rambo(AssemblyNode):
    """Board, cover, and the stack of spacers between them and the panel.

    At each of the four corners: two lasercut spacers hold the board
    off the panel, a hex spacer holds the cover off the board, and a
    bolt closes the stack.  Drawn in the left panel's own plane.

    Each of those three is one part repeated over the four corners.
    """

    connector_position = (100, 60)

    panel_spacers = DoubleM3Spacer().repeat(len(CORNERS))
    cover_spacers = HexSpacer32mm().repeat(len(CORNERS))
    cover_bolts = CoverBolt().repeat(len(CORNERS))
    board = RamboPcb()
    connector = PsuConnector()
    cover = RamboCover()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        board_deck = 2 * thickness
        cover_deck = board_deck + RAMBo_pcb_thickness

        for corner, (x, y) in enumerate(CORNERS):
            self.panel_spacers[corner].translate([x, y, 0])
            self.cover_spacers[corner].translate([x, y, cover_deck])
            self.cover_bolts[corner].translate(
                [x, y, cover_deck + hexspacer_length + RAMBo_cover_thickness])

        self.board.translate([0, 0, board_deck])
        self.connector.translate(
            [self.connector_position[0], self.connector_position[1],
             cover_deck])
        self.cover.translate([0, 0, cover_deck + hexspacer_length])
