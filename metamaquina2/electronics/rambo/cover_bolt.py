"""The bolt that holds the RAMBo cover down."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart, curve
from metamaquina2.params import M3_bolt_head


class CoverBolt(ScadPart):
    """One M3x10 into a hex spacer.

    The design draws only the head, as a plain cylinder, so that is
    what this renders -- the part is real, its shank is simply not
    modelled.
    """

    color = materials.METAL
    head_radius = 3

    def render(self):
        return curve('cylinder', r=self.head_radius, h=M3_bolt_head)
