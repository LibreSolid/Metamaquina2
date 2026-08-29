"""The Y axis belt."""

from molejo import P, Shape, Wrap
from solid_node.node import TranslationalPort

from metamaquina2 import gt2
from metamaquina2.params import (
    IdlerRadius,
    RightPanel_basewidth,
    bar_cut_length,
    base_bars_Zdistance,
    belt_width,
)


# The three bearings the loop runs on, in the belt's own plane: +x runs
# from the rear of the machine towards the front and +y runs upwards,
# which is the plane the design draws the loop in.  The two upper ones
# are the idlers on the front and rear horizontal bars; the third is the
# one on the lower rear bar, which pulls the run down to the motor.
FRONT = [RightPanel_basewidth / 2 - bar_cut_length, 0]
REAR = [-RightPanel_basewidth / 2 + bar_cut_length, 0]
LOWER = [REAR[0] + 30, -base_bars_Zdistance]

#: The pitch circles, ordered clockwise seen from +Z.
#:
#: The design lists the three the other way round.  molejo runs a wrap
#: clockwise, so they are listed reversed here: the same loop on the
#: same three bearings, run the way molejo runs it, which puts the
#: bed's own run last.
#:
#: All three are bare 608 bearings, so the belt rides every one of them
#: on its tooth tips: there is no toothed pulley anywhere in the loop
#: the design draws, and the motor at the rear reaches it through
#: geometry the design does not model.
CIRCLES = [
    gt2.on_idler(FRONT, IdlerRadius),
    gt2.on_idler(LOWER, IdlerRadius),
    gt2.on_idler(REAR, IdlerRadius),
]

#: The upper run between the two bar idlers, which the platform's four
#: clamps grip -- and the last of the three spans, because reversing the
#: order moved it to the end.
CLAMP_SPAN = 2

#: Where along the run it begins: the tangent point on the rear idler,
#: in the belt's own plane, which a bed position is measured from to
#: reach the anchor.
CLAMP_ORIGIN = gt2.span_origin(CIRCLES, CLAMP_SPAN)[0]


class YBelt(gt2.Belt):
    """The GT2 loop around the three bar idlers, clamped under the bed.

    The loop stands still -- its three bearings are bolted to the frame
    -- and the bed drags the belt's material through it.  So the shape
    is re-drawn at every bed position rather than moved, which is what
    the `clamp` parameter is: where along the upper run the platform
    holds the belt.

    The design puts four clamp plates under the platform, two stacked at
    each of two points either side of its centre, pinching the belt
    between them.  The belt is continuous between them, so the number
    the loop needs is the platform's own centre.
    """

    clamp = TranslationalPort(
        unit='mm', scale=gt2.span_scale(CIRCLES, CLAMP_SPAN))

    def render(self):
        return Shape(
            profile=gt2.section(belt_width),
            path=[Wrap(around=CIRCLES,
                       teeth=gt2.teeth(CIRCLES),
                       anchor={'span': CLAMP_SPAN, 'at': P.clamp})],
            path_samples=gt2.PATH_SAMPLES,
            profile_samples=4,
            loop=True,
        )
