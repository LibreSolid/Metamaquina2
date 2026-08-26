"""One of the five plates the extruder body is stacked from."""

from metamaquina2.part import SheetPart
from metamaquina2 import scad


class ExtruderSlice(SheetPart):
    """A single slice of the extruder block.

    The body is not machined out of one piece: it is five different
    profiles cut from the same sheet stock and stacked, so the
    filament channel, the bearing pockets and the nut traps all fall
    out of the stack.  Each slice is its own part, and the number
    selects which profile is cut.
    """

    count = 5

    def __init__(self, number, **kwargs):
        if not 1 <= number <= self.count:
            raise ValueError(
                f'the extruder block has slices 1..{self.count}, '
                f'not {number}')
        self.number = number
        super().__init__(number, **kwargs)

    def profile(self):
        return getattr(scad.extruder, f'slice{self.number}_face')()
