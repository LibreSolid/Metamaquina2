"""The t-slot hardware that bolts the frame's panels to each other."""

from solid_node.node import AssemblyNode

from metamaquina2 import frames
from metamaquina2.frame.tslot_bolt import TSlotBolt
from metamaquina2.params import (
    SidePanel_TSLOTS,
    TopPanel_TSLOTS,
    thickness,
)


def _place(bolt, slot):
    """Put a t-slot bolt at one entry of a slot table.

    A table entry is `[x, y, width, angle]` in the plane of the sheet
    being bolted, and the bolt goes in the middle of the slot.
    """
    x, y, width, angle = slot
    return (bolt
            .translate([0, width / 2, 0])
            .rotate(angle, [0, 0, 1])
            .translate([x, y, 0]))


class PanelJoints(AssemblyNode):
    """Every t-slot bolt in the frame.

    A t-slot joint is a bolt through a slot in one sheet into a nut
    captive in the edge of another, and it belongs to neither sheet --
    it is what makes them one frame.  The same table of slots serves
    both side panels; the right panel is bolted from its far face, so
    its bolts are flipped and offset by the panel's thickness.

    Every bolt of a side is the same fastener, so each side is one
    declaration repeated as many times as its table has entries, and
    the table is read in `render` where the placements belong.  Nothing
    here moves -- a bolt through a sheet stays where it is put -- and a
    rest render is run once, so each is put there once.
    """

    left = TSlotBolt().repeat(len(SidePanel_TSLOTS))
    right = TSlotBolt(flipped=True).repeat(len(SidePanel_TSLOTS))
    top = TSlotBolt().repeat(len(TopPanel_TSLOTS))

    def render(self):
        for bolt, slot in zip(self.left, SidePanel_TSLOTS):
            frames.left_panel(_place(bolt, slot))
        for bolt, slot in zip(self.right, SidePanel_TSLOTS):
            frames.right_panel(
                _place(bolt, slot).translate([0, 0, thickness]))
        for bolt, slot in zip(self.top, TopPanel_TSLOTS):
            frames.top_panel(_place(bolt, slot))
