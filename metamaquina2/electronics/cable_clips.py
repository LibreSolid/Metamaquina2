"""Every cable clip in the machine, on the panel it sticks to."""

from solid_node.node import AssemblyNode

from metamaquina2 import frames
from metamaquina2.electronics.cable_clip import CableClip
from metamaquina2.params import (
    bottom_cable_clips,
    left_cable_clips,
    right_cable_clips,
    thickness,
    top_cable_clips,
)


def _under(clip):
    """A clip stuck to the underside of the panel it is listed for."""
    kind, angle, x, y = clip
    return (CableClip(kind)
            .rotate(180, [1, 0, 0])
            .rotate(angle, [0, 0, 1])
            .translate([x, y, 0]))


def _over(clip):
    """A clip stuck to the far face of the panel it is listed for."""
    kind, angle, x, y = clip
    return (CableClip(kind)
            .rotate(angle, [0, 0, 1])
            .translate([x, y, thickness]))


class CableClips(AssemblyNode):
    """The clips that route the loom around the machine.

    Each panel has its own table of clips in the design, given in that
    panel's flat plane, so each table is read and handed to that
    panel's frame.  The right panel's clips sit on the outer face; the
    rest hang under theirs.
    """

    def __init__(self, *args, **kwargs):
        self.left = [frames.left_panel(_under(clip))
                     for clip in left_cable_clips]
        self.right = [frames.right_panel(_over(clip))
                      for clip in right_cable_clips]
        self.top = [frames.top_panel(_under(clip))
                    for clip in top_cable_clips]
        self.bottom = [frames.bottom_panel(_under(clip))
                       for clip in bottom_cable_clips]
        super().__init__(*args, **kwargs)

    def render(self):
        return self.left + self.right + self.top + self.bottom
