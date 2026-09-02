"""The extruder body: five slices stacked."""

from solid_node.node import AssemblyNode

from metamaquina2.params import thickness
from metamaquina2.x_stage.carriage.extruder.slice import ExtruderSlice


def _slices():
    """One declaration per slice of the block.

    A helper rather than a comprehension written in the class body: a
    comprehension there is inlined into the body's own frame, which
    hides the body from the framework and builds shared instances
    instead of declarations.
    """
    return [ExtruderSlice(number=number)
            for number in range(1, ExtruderSlice.count + 1)]


class ExtruderBlock(AssemblyNode):
    """The five slices, bolted through as one block.

    They are bolted, not glued, so this is an assembly: five parts a
    builder stacks in order and pulls together with five M3x35.
    """

    slices = _slices()

    def render(self):
        for number, slice_ in enumerate(self.slices, start=1):
            slice_.translate([0, 0, (number - 1) * thickness])
