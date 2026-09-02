"""The extruder body: five slices stacked."""

from solid_node.node import AssemblyNode

from metamaquina2.params import thickness
from metamaquina2.x_stage.carriage.extruder.slice import ExtruderSlice


class ExtruderBlock(AssemblyNode):
    """The five slices, bolted through as one block.

    They are bolted, not glued, so this is an assembly: five parts a
    builder stacks in order and pulls together with five M3x35.
    """

    slices = [ExtruderSlice(number=number)
              for number in range(1, ExtruderSlice.count + 1)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for number, slice_ in enumerate(self.slices, start=1):
            slice_.translate([0, 0, (number - 1) * thickness])
