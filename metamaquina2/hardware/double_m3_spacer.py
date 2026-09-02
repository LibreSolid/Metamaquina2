"""Two lasercut M3 spacers, stacked."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.m3_spacer import M3Spacer
from metamaquina2.params import thickness


class DoubleM3Spacer(AssemblyNode):
    """The design's `double_M3_lasercut_spacer`: two separate pieces.

    They are stacked, not fused -- each is cut on its own and the two
    are only held together by the bolt through them, so this is an
    assembly of two spacers rather than one part twice as thick.
    """

    lower = M3Spacer()
    upper = M3Spacer()

    def render(self):
        self.upper.translate([0, 0, thickness])
