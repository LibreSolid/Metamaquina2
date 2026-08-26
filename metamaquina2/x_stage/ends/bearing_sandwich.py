"""The bearing sandwich of an X end: a plate and the spacers behind it."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.double_m3_spacer import DoubleM3Spacer
from metamaquina2.params import bearing_sandwich_spacing, thickness
from metamaquina2.x_stage.ends.sandwich_plate import XEndSandwichPlate


class XEndBearingSandwich(AssemblyNode):
    """What holds the two Z bearings against the back plate.

    Four pairs of stacked spacers set the gap and one plate closes it,
    so the bearings are clamped rather than glued in.  It stands on
    edge: the plate faces along the beam.
    """

    spacer_holes = ((-14, 0), (-14, 45), (14, 0), (14, 45))

    def __init__(self, *args, **kwargs):
        def standing(node, offset):
            return (node
                    .rotate(90, [0, 0, 1])
                    .rotate(90, [0, 1, 0])
                    .translate([offset, 0, 0]))

        self.spacers = [
            standing(DoubleM3Spacer().translate([x, y, 0]), thickness)
            for x, y in self.spacer_holes
        ]
        self.plate = standing(XEndSandwichPlate(),
                              thickness + bearing_sandwich_spacing)

        super().__init__(*args, **kwargs)

    def render(self):
        return self.spacers + [self.plate]
