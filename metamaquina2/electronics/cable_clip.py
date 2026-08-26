"""A stick-on cable clip."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import cable_clips


class CableClip(ScadPart):
    """One Hellermann right-angle clip, in whichever size is called for.

    The machine uses three sizes -- RA6, RA9 and RA13 -- and the design
    picks them from tables of positions per panel.  The size is a
    constructor argument, so each size is its own part with its own
    artifacts.
    """

    color = materials.NYLON

    def __init__(self, kind, **kwargs):
        self.kind = kind
        super().__init__(kind, **kwargs)

    def render(self):
        return cable_clips.cable_clip(self.kind)
