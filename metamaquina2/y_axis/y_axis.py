"""The Y axis."""

from solid_node.node import AssemblyNode

from metamaquina2.params import (
    base_bars_Zdistance,
    base_bars_height,
    belt_width,
)
from metamaquina2.y_axis import y_belt
from metamaquina2.y_axis.motor.y_motor import YMotor
from metamaquina2.y_axis.platform.y_platform import YPlatform
from metamaquina2.y_axis.y_belt import YBelt
from metamaquina2.y_axis.y_rods import YRods


class YAxis(AssemblyNode):
    """The bed axis: rods, platform, belt and motor.

    The rods are clamped to the frame's horizontal bars, the platform
    rides them, and the belt runs from the motor at the back, around
    the idlers on those same bars, to the clamps under the platform.

    Only the platform moves, and only the pulley turns, both off the
    motor's own shaft: the two sentences below say so, in the belt's
    own plane, where the loop's x runs from the rear of the machine
    forwards, against the machine's y -- the sign the two ratios differ
    by.  The motor is bolted to the frame and the belt loop stands
    where its three idlers and that pulley hold it -- but the belt
    inside that loop does follow the bed, so it takes the bed's
    position too and re-draws itself from it rather than being placed.
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

    rods = YRods()
    platform = YPlatform()
    belt = YBelt()
    motor = YMotor()

    #: The motor shaft's own angle drives the belt's clamp and the
    #: platform's slide alike, at the pitch arc's rate.  The two ratios
    #: differ in sign because the loop's x runs against the machine's
    #: y; `PULLEY_AT_ORIGIN` is the shaft's own angle with the clamp at
    #: nought, and `CLAMP_ORIGIN` is the extra term the platform's own
    #: rest and the belt's own anchor differ by.
    motor.shaft.drives(
        belt.clamp,
        ratio=y_belt.BED_PER_DEGREE,
        offset=-y_belt.PULLEY_AT_ORIGIN * y_belt.BED_PER_DEGREE)
    motor.shaft.drives(
        platform.slide,
        ratio=-y_belt.BED_PER_DEGREE,
        offset=(y_belt.PULLEY_AT_ORIGIN * y_belt.BED_PER_DEGREE
                - y_belt.CLAMP_ORIGIN))

    def render(self):
        """Stand the belt loop where its idlers and its pulley hold it.

        The loop does not go anywhere -- both its ends are bolted under
        the platform -- so where it stands in the machine is said here.
        What travels inside it is told to it every instant, as a port.
        """
        (self.belt
         .rotate(90, [1, 0, 0])
         .rotate(-90, [0, 0, 1])
         .translate(self.belt_position))
