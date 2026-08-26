"""The Y axis."""

from solid_node.node import AssemblyNode

from metamaquina2.params import XZStage_offset, YCarPosition
from metamaquina2.y_axis.motor.y_motor import YMotor
from metamaquina2.y_axis.platform.y_platform import YPlatform
from metamaquina2.y_axis.y_belt import YBelt
from metamaquina2.y_axis.y_rods import YRods


class YAxis(AssemblyNode):
    """The bed axis: rods, platform, belt and motor.

    The rods are clamped to the frame's horizontal bars, the platform
    rides them, and the belt runs from the motor at the back, around
    the idlers on those same bars, to the clamps under the platform.
    """

    # where the belt loop stands in the machine
    belt_position = [2.5, 0, 66]

    def __init__(self, *args, **kwargs):
        self.rods = YRods()
        self.platform = YPlatform().translate(
            [0, YCarPosition - XZStage_offset, 0])
        self.belt = (YBelt()
                     .rotate(90, [1, 0, 0])
                     .rotate(-90, [0, 0, 1])
                     .translate(self.belt_position))
        self.motor = YMotor()
        super().__init__(*args, **kwargs)

    def render(self):
        return [self.rods, self.platform, self.belt, self.motor]
