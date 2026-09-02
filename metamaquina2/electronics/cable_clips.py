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


def _under(clip, entry):
    """Stick a clip to the underside of the panel it is listed for."""
    kind, angle, x, y = entry
    return (clip
            .rotate(180, [1, 0, 0])
            .rotate(angle, [0, 0, 1])
            .translate([x, y, 0]))


def _over(clip, entry):
    """Stick a clip to the far face of the panel it is listed for."""
    kind, angle, x, y = entry
    return (clip
            .rotate(angle, [0, 0, 1])
            .translate([x, y, thickness]))


class CableClips(AssemblyNode):
    """The clips that route the loom around the machine.

    Each panel has its own table of clips in the design, given in that
    panel's flat plane, so each table is read and handed to that
    panel's frame.  The right panel's clips sit on the outer face; the
    rest hang under theirs.

    The three sizes are three different parts, so each table becomes
    an enumerated list -- one clip declared per entry, read straight
    off the design's own table -- rather than one repeated
    declaration.
    """

    left = [CableClip(kind)
            for kind, _angle, _x, _y in left_cable_clips]
    right = [CableClip(kind)
             for kind, _angle, _x, _y in right_cable_clips]
    top = [CableClip(kind)
           for kind, _angle, _x, _y in top_cable_clips]
    bottom = [CableClip(kind)
              for kind, _angle, _x, _y in bottom_cable_clips]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for clip, entry in zip(self.left, left_cable_clips):
            frames.left_panel(_under(clip, entry))
        for clip, entry in zip(self.right, right_cable_clips):
            frames.right_panel(_over(clip, entry))
        for clip, entry in zip(self.top, top_cable_clips):
            frames.top_panel(_under(clip, entry))
        for clip, entry in zip(self.bottom, bottom_cable_clips):
            frames.bottom_panel(_under(clip, entry))
