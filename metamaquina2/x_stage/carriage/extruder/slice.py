"""One of the five plates the extruder body is stacked from."""

from solid_node.parameters import Count

from metamaquina2.part import SheetPart
from metamaquina2 import scad


class ExtruderSlice(SheetPart):
    """A single slice of the extruder block.

    The body is not machined out of one piece: it is five different
    profiles cut from the same sheet stock and stacked, so the
    filament channel, the bearing pockets and the nut traps all fall
    out of the stack.  Each slice is its own part, and the number
    selects which profile is cut -- declared, so the range the block
    has is a constraint rather than a hand-written check.
    """

    count = 5

    number = Count(min=1, max=count)

    def profile(self):
        return getattr(scad.extruder, f'slice{self.number}_face')()
