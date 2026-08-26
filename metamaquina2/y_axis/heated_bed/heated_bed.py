"""The heated build platform: board plus glass."""

from solid_node.node import AssemblyNode

from metamaquina2.params import (
    glass_h,
    glass_w,
    heated_bed_pcb_thickness,
)
from metamaquina2.y_axis.heated_bed.glass import HeatedBedGlass
from metamaquina2.y_axis.heated_bed.pcb import HeatedBedPcb


class HeatedBed(AssemblyNode):
    """The board and the glass on top of it.

    Two separate parts, clipped together rather than bonded -- the
    glass comes off to release a print -- so they are an assembly.
    The design's silkscreen outline is not modelled here: it is ink on
    the board, not a part.
    """

    def __init__(self, *args, **kwargs):
        self.pcb = HeatedBedPcb()
        self.glass = HeatedBedGlass().translate(
            [-glass_w / 2, -glass_h / 2, heated_bed_pcb_thickness])
        super().__init__(*args, **kwargs)

    def render(self):
        return [self.pcb, self.glass]
