"""The Y axis belt, and the phase of the pulley it meshes on."""

import math

from molejo import P, Shape, Wrap
from solid_node.node import TranslationalPort

from metamaquina2 import gt2
from metamaquina2.hardware.gt2_pulley import TEETH
from metamaquina2.params import (
    IdlerRadius,
    RightPanel_basewidth,
    bar_cut_length,
    base_bars_Zdistance,
    base_bars_height,
    belt_width,
)
from metamaquina2.y_axis.motor.mount import SHAFT


# The four things the loop runs on, in the belt's own plane: +x runs
# from the rear of the machine towards the front and +y runs upwards,
# which is the plane the design draws the loop in.  The two upper
# bearings are the idlers on the front and rear horizontal bars; the
# third is the one on the lower rear bar; and between those last two
# stands the motor pulley.
FRONT = [RightPanel_basewidth / 2 - bar_cut_length, 0]
REAR = [-RightPanel_basewidth / 2 + bar_cut_length, 0]
LOWER = [REAR[0] + 30, -base_bars_Zdistance]

#: The motor shaft, in the same plane: the machine's Y read backwards,
#: because the loop's x runs against it, and its Z measured down from
#: the upper bars the loop is placed at.
PULLEY = [-SHAFT[0], SHAFT[1] - base_bars_height - base_bars_Zdistance]

#: How far a radius may still move before the loop is called closed.
#:
#: A picometre, as on the X belt, and reached in about six turns of the
#: iteration below.
CLOSED = 1e-12


def _circles(pulley_radius):
    """The pitch circles, ordered clockwise seen from +Z.

    The design lists its three bearings the other way round; molejo runs
    a wrap clockwise, so they are reversed here and the bed's own run
    comes last.

    Three of the four are bare 608 bearings and the belt runs its smooth
    back on them, which is what its teeth facing outward means.  The
    fourth is the motor pulley, and the belt is bent backwards over it:
    the two rear bearings are 58 mm apart with the pulley 40 mm inside
    the line between them, so the belt leaves the upper one on an
    internal tangent, hugs the pulley from the far side through about
    156 degrees, and crosses back out to the lower one.  That reverse
    bend is what puts the teeth against the pulley -- the belt turns the
    other way there, and the face that meets a circle turns with it --
    and it is the whole of how this axis is driven.
    """
    return [
        gt2.on_idler(FRONT, IdlerRadius, face='outer'),
        gt2.on_idler(LOWER, IdlerRadius, face='outer'),
        gt2.on_pulley(PULLEY, pulley_radius, turn='counterclockwise'),
        gt2.on_idler(REAR, IdlerRadius, face='outer'),
    ]


def _meshed_radius():
    """Where the motor pulley's flanks stand, for a belt whose teeth are
    spaced exactly as its grooves are.

    The X belt's own circular argument, run round this loop: a pulley of
    a given tooth count has a radius only once its grooves have a pitch,
    molejo draws a loop's teeth at the loop's length over a whole tooth
    count, and the loop is not drawn until the pulley it wraps has a
    radius.  Closed by iteration from the nominal pitch, and worth the
    same thing here: only when the two pitch circles are the same circle
    is one tooth of belt exactly one groove of pulley.
    """
    radius = gt2.pulley_radius(TEETH)
    while True:
        closer = gt2.pulley_radius(TEETH, gt2.pitch(_circles(radius)))
        if abs(closer - radius) < CLOSED:
            return closer
        radius = closer


#: Where the pulley's flanks stand: the same 4.839 the X end is
#: dimensioned from, because it is the same bought pulley, derived again
#: from the tooth count against this loop's own pitch.
PULLEY_RADIUS = _meshed_radius()

#: The pitch circles the loop is drawn around.
CIRCLES = _circles(PULLEY_RADIUS)

#: The pitch the loop's teeth come out at, and so the pitch this pulley
#: is cut at -- not quite the standard's 2 mm, for the reason `gt2.pitch`
#: gives.
PERIOD = gt2.pitch(CIRCLES)

#: Where each element of the loop begins, in belt.
STATIONS = gt2.stations(CIRCLES)

#: The upper run between the two bar idlers, which the platform's four
#: clamps grip -- the last of the four spans, because reversing the
#: bearings' order moved it to the end.
CLAMP_SPAN = 3

#: The arc about the pulley: element 3 of the eight, since the elements
#: run span, arc, span, arc and the pulley is the third circle.
PULLEY_ARC = 3

#: Where along the run the clamped span begins: the tangent point on the
#: rear idler, in the belt's own plane, which a bed position is measured
#: from to reach the anchor.
CLAMP_ORIGIN = gt2.span_origin(CIRCLES, CLAMP_SPAN)[0]

#: Where on the pulley the belt first touches it, as an angle about the
#: pulley's centre: the end of the span that arrives, and so the angle a
#: tooth sitting exactly at that station would stand at.
#:
#: Taken in [0, 2*pi) rather than as `atan2` returns it, and that is not
#: cosmetic.  A pulley's angle is modulo a whole turn anyway -- modulo a
#: groove, in fact, since sixteen of them are alike -- so either number
#: says the same thing to the geometry.  But this one is the constant
#: the serialized expression leads with, and the viewer's expression
#: evaluator (jokenizer 0.4.5, through `solid_node.viewers.widget`)
#: parses subtraction right-associatively: it reads `-a + b` as
#: `-(a + b)` and `1 - 2 - 3` as 2.  A negative lead constant therefore
#: negates the whole angle in the browser, which flips the *rate* along
#: with it -- the pulley spins backwards there while every Python test
#: passes, because Python's arithmetic is not jokenizer's.  Keeping the
#: constant positive keeps the expression out of the one shape that
#: parser gets wrong.  The defect is the framework's and wants fixing
#: there; this only keeps this machine out of its way, and is written
#: down so nobody tidies it back.
_ARRIVAL = gt2.spans(CIRCLES)[1]
_TOUCH = (_ARRIVAL[0][0] + _ARRIVAL[1][0] * _ARRIVAL[2],
          _ARRIVAL[0][1] + _ARRIVAL[1][1] * _ARRIVAL[2])
PULLEY_PHASE = math.atan2(_TOUCH[1] - PULLEY[1],
                          _TOUCH[0] - PULLEY[0]) % (2 * math.pi)


def pulley_angle(position):
    """Which way the motor pulley faces with the bed at `position`,
    measured in the belt's own plane rather than the machine's.

    The bed is not what drives this pulley on the machine -- it is the
    other way round, and the belt is what joins them -- but the belt is
    drawn from the bed, so the angle that keeps a groove under every
    tooth is read from the bed too.

    Two conversions and a division, as on the X belt.  A bed position
    becomes a length of belt the way `YBelt.clamp` does it, from the
    start of the clamped run and through that run's own tilt; the
    pulley's own arc begins at a known station, so the difference is how
    much belt has gone by since the belt touched it; and that length
    becomes an angle at the pulley's pitch radius.

    Added rather than subtracted, which is the reverse bend showing up
    as a sign: the belt turns counterclockwise about this pulley where
    it turns clockwise about every other circle in the loop, so belt
    running on carries a tooth the other way round it.

    The loop's own length drops out of it.  It is a whole number of
    teeth by construction, so it is a whole number of this pulley's
    grooves too, and the pulley cannot tell one from another.

    Written as arithmetic rather than through `math.degrees`, because
    `position` is not always a number: the serialization pass drives the
    tree symbolically, and what comes through then is an expression in
    the machine's own `y` for the viewer to turn the pulley by.
    """
    anchor = (position - CLAMP_ORIGIN) * gt2.span_scale(CIRCLES, CLAMP_SPAN)
    gone = STATIONS[2 * CLAMP_SPAN] + anchor - STATIONS[PULLEY_ARC]
    turn = PULLEY_PHASE + gone / (PULLEY_RADIUS + gt2.PITCH_LINE)
    return turn * 180 / math.pi


class YBelt(gt2.Belt):
    """The GT2 loop around the three bar idlers and the motor pulley,
    clamped under the bed.

    The loop stands still -- its three bearings and the motor are all
    bolted to the frame -- and the bed drags the belt's material through
    it.  So the shape is re-drawn at every bed position rather than
    moved, which is what the `clamp` parameter is: where along the upper
    run the platform holds the belt.

    The design puts four clamp plates under the platform, two stacked at
    each of two points either side of its centre, pinching the belt
    between them.  The belt is continuous between them, so the number
    the loop needs is the platform's own centre.

    Its teeth are outward, which is the one thing that distinguishes it
    from the X loop and the thing that makes it a drive at all.  The
    three bearings then carry the belt on its smooth back, as bare races
    should, and the toothed face is the one that comes round onto the
    pulley at the reverse bend.
    """

    clamp = TranslationalPort(
        unit='mm', scale=gt2.span_scale(CIRCLES, CLAMP_SPAN))

    def render(self):
        return Shape(
            profile=gt2.section(belt_width, face='outer'),
            path=[Wrap(around=CIRCLES,
                       teeth=gt2.teeth(CIRCLES, face='outer'),
                       anchor={'span': CLAMP_SPAN, 'at': P.clamp})],
            path_samples=gt2.PATH_SAMPLES,
            profile_samples=4,
            loop=True,
        )
