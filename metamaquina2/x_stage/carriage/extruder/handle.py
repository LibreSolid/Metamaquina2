"""The idler release handle and the bolts it pivots on."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bolt import Bolt
from metamaquina2.params import (
    HandleWidth,
    handle_bolt_length,
    handle_nut_height,
)
from metamaquina2.x_stage.carriage.extruder.handle_plate import HandlePlate


class Handle(AssemblyNode):
    """The lever and the two long M4 bolts that run through it.

    Squeezing the lever compresses the springs on those bolts and lets
    the idler swing away from the hobbed bolt, so filament can be
    pushed in or pulled out.
    """

    def __init__(self, *args, **kwargs):
        self.plate = HandlePlate()
        self.bolts = [
            Bolt(4, handle_bolt_length).translate(
                [side * HandleWidth / 6, 5,
                 handle_bolt_length - handle_nut_height])
            for side in (-1, 1)
        ]
        super().__init__(*args, **kwargs)

    def render(self):
        return [self.plate] + self.bolts
