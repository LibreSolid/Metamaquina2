"""The Y axis."""

from solid_node.node import AssemblyNode, TranslationalPort

from metamaquina2.params import XZStage_offset
from metamaquina2.y_axis.motor.y_motor import YMotor
from metamaquina2.y_axis.platform.y_platform import YPlatform
from metamaquina2.y_axis.y_belt import YBelt
from metamaquina2.y_axis.y_rods import YRods


class YAxis(AssemblyNode):
    """The bed axis: rods, platform, belt and motor.

    The rods are clamped to the frame's horizontal bars, the platform
    rides them, and the belt runs from the motor at the back, around
    the idlers on those same bars, to the clamps under the platform.

    Where the bed stands along the rods comes in through
    `platform_position`, in the same Y coordinate the design uses, and
    the machine is what wires it.  So this axis no longer builds on its
    own: an unconnected port has no value, and asking for one says so
    rather than drawing the bed somewhere nobody chose.

    Only the platform moves.  The motor is bolted to the frame and the
    belt loop keeps the shape it has in the design -- a belt that
    really followed the bed would have to be re-drawn, not re-placed.
    """

    # where the belt loop stands in the machine
    belt_position = [2.5, 0, 66]

    platform_position = TranslationalPort(unit='mm')

    def __init__(self, *args, **kwargs):
        self.rods = YRods()
        self.platform = YPlatform()
        self.belt = (YBelt()
                     .rotate(90, [1, 0, 0])
                     .rotate(-90, [0, 0, 1])
                     .translate(self.belt_position))
        self.motor = YMotor()
        super().__init__(*args, **kwargs)

    def render(self):
        """Stand the bed where the machine put it.

        The offset is the axis' own: the platform is drawn about the
        origin and the whole X/Z stage sits `XZStage_offset` off it, so
        a bed at Y nought still has to be moved back by that much to be
        under the nozzle.
        """
        self.platform.translate(
            [0, self.platform_position.value - XZStage_offset, 0])

        return [self.rods, self.platform, self.belt, self.motor]
