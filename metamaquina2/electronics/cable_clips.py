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


def _clips(table):
    """One clip declaration per entry of a panel's table.

    A module-level helper rather than a comprehension written in the
    class body: a comprehension there is inlined into the body's own
    frame with a plain dict for its locals, so the framework cannot
    see that a class body is executing and builds shared node
    instances instead of declarations.
    """
    return [CableClip(kind) for kind, _angle, _x, _y in table]


class CableClips(AssemblyNode):
    """The clips that route the loom around the machine.

    Each panel has its own table of clips in the design, given in that
    panel's flat plane, so each table is read and handed to that
    panel's frame.  The right panel's clips sit on the outer face; the
    rest hang under theirs.

    The three sizes are three different parts, so each table becomes a
    literal list of the clips it names rather than one repeated
    declaration.
    """

    left = _clips(left_cable_clips)
    right = _clips(right_cable_clips)
    top = _clips(top_cable_clips)
    bottom = _clips(bottom_cable_clips)

    def render(self):
        for clip, entry in zip(self.left, left_cable_clips):
            frames.left_panel(_under(clip, entry))
        for clip, entry in zip(self.right, right_cable_clips):
            frames.right_panel(_over(clip, entry))
        for clip, entry in zip(self.top, top_cable_clips):
            frames.top_panel(_under(clip, entry))
        for clip, entry in zip(self.bottom, bottom_cable_clips):
            frames.bottom_panel(_under(clip, entry))
