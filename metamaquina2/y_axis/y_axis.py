"""The Y axis."""

from solid_node.node import AssemblyNode, TranslationalPort

from metamaquina2.params import (
    XZStage_offset,
    base_bars_Zdistance,
    base_bars_height,
    belt_width,
)
from metamaquina2.y_axis.motor.y_motor import YMotor
from metamaquina2.y_axis.platform.y_platform import YPlatform
from metamaquina2.y_axis.y_belt import CLAMP_ORIGIN, YBelt, pulley_angle
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

    Only the platform moves, and only the pulley turns.  The motor is
    bolted to the frame and the belt loop stands where its three idlers
    and that pulley hold it -- but the belt inside that loop does follow
    the bed, so it takes the bed's position too and re-draws itself from
    it rather than being placed, and the pulley takes it a third way, as
    the angle that keeps a groove under every tooth coming round onto
    it.
    """

    # Where the belt loop stands in the machine: centred across the
    # bearings it runs on, and at the height of the upper horizontal
    # bars that carry two of the three.
    #
    # The design writes that height down as a literal 66, one
    # millimetre below where its own bars put those bearings.  Nothing
    # showed while the belt was a 2 mm ring hulled around three circles
    # -- it simply sat a millimetre low and touched nothing.  A belt
    # with teeth on it is drawn to the radius it really rides at, and a
    # millimetre of that goes straight through the outer race.  So the
    # height is derived here from the same two numbers the bars are
    # placed by, which is what this layer is for.
    belt_position = [belt_width / 2, 0,
                     base_bars_height + base_bars_Zdistance]

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
        """Stand the bed where the machine put it, tell the belt where
        it is being held, and turn the pulley to meet it.

        The offset is the axis' own: the platform is drawn about the
        origin and the whole X/Z stage sits `XZStage_offset` off it, so
        a bed at Y nought still has to be moved back by that much to be
        under the nozzle.

        The belt is told the same position in its own plane, which the
        assembly turns a quarter turn to stand up: the loop's x runs
        from the rear of the machine forwards, against the machine's y,
        so the bed's coordinate is negated before the tangent point on
        the rear idler is taken off it.  The pulley is told that same
        negated coordinate, because `y_belt` measures its angle in the
        loop's plane too.
        """
        placed = self.platform_position.value - XZStage_offset

        self.platform.translate([0, placed, 0])

        self.connect(-placed - CLAMP_ORIGIN, self.belt.clamp)

        self.connect(pulley_angle(-placed), self.motor.shaft)

        return [self.rods, self.platform, self.belt, self.motor]
