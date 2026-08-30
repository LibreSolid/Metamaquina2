"""The X axis belt, and the phase of the pulley it meshes on."""

import math

from molejo import P, Shape, Wrap
from solid_node.node import TranslationalPort

from metamaquina2 import gt2
from metamaquina2.hardware.gt2_pulley import TEETH
from metamaquina2.params import (
    IdlerRadius,
    XEnd_box_size,
    XIdler_height,
    XMotor_height,
    belt_width,
    machine_x_dim,
    thickness,
)


# The two things the loop runs on, in the belt's own plane: +x along the
# beam and +y up, which is the plane the design draws the loop in.
PULLEY = [-machine_x_dim / 2 + thickness + XEnd_box_size / 2, XMotor_height]
IDLER = [machine_x_dim / 2 - thickness - XEnd_box_size / 2, XIdler_height]

#: How far a radius may still move before the loop is called closed.
#:
#: A picometre.  The iteration below converges by about four decimal
#: places a turn, so this is reached in six of them and is a statement
#: that the loop has stopped moving rather than a tolerance anything is
#: allowed within.
CLOSED = 1e-12


def _meshed_radius():
    """Where the motor pulley's flanks stand, for a belt whose teeth are
    spaced exactly as its grooves are.

    The two ends of that sentence chase each other.  A pulley of a given
    tooth count has a radius only once its grooves have a pitch; molejo
    draws a loop's teeth at the loop's length over a whole tooth count,
    so that pitch is not known until the loop is drawn; and the loop is
    not drawn until the pulley it wraps has a radius.  So the circle is
    closed by iteration from the nominal pitch, a quarter of a micron
    from where it lands.

    What it buys is not clearance -- the pulley has its own, and would
    swallow this either way -- but a ratio.  Only when the belt's pitch
    circle and the pulley's are the same circle is a tooth of belt
    exactly one groove of pulley: drawn at the nominal 2 mm instead, a
    tooth turns the motor 17.996 degrees rather than 18, and a drive
    that is a fortieth of a percent out is a drive with a number in it
    that nothing chose.
    """
    radius = gt2.pulley_radius(TEETH)
    while True:
        circles = [gt2.on_pulley(PULLEY, radius),
                   gt2.on_idler(IDLER, IdlerRadius)]
        closer = gt2.pulley_radius(TEETH, gt2.pitch(circles))
        if abs(closer - radius) < CLOSED:
            return closer
        radius = closer


#: Where the pulley's flanks stand: 4.839, within a micron of the
#: `PulleyRadius` the design now derives the whole X end from.
#:
#: Derived here from the tooth count rather than read off `params`, and
#: the two agreeing is a contract the tests hold rather than a
#: coincidence.  They did not agree before: the design wrote a round 6,
#: which is no pulley at all -- it asks for 19.66 teeth -- and the belt
#: was drawn around it because there was no pulley to disagree, the
#: design's module drawing nothing.  What the design buys is a 16 tooth
#: pulley, and the number was corrected to it.  The idler end keeps the
#: design's own radius, because a 608 bearing really is 11 mm and has
#: nothing to mesh.
PULLEY_RADIUS = _meshed_radius()

#: The pitch circles, ordered clockwise seen from +Z, which is the order
#: molejo runs a wrap in: motor at the left, idler at the right, so the
#: first tangent span is the upper run travelling towards the idler.
#:
#: The two radii are converted differently because the two parts are
#: different.  The motor end carries a toothed pulley and the belt
#: meshes with it; the idler end is a bare 608 bearing and the belt
#: rides it on its tooth tips, back-side out.  The design draws both
#: with the belt's inner surface exactly on the circle, which is why its
#: two heights are set so those surfaces line up; a real belt's pitch
#: line does not, and the upper run comes out very slightly tilted.
CIRCLES = [
    gt2.on_pulley(PULLEY, PULLEY_RADIUS),
    gt2.on_idler(IDLER, IdlerRadius),
]

#: The pitch the loop's teeth come out at, and so the pitch the pulley
#: is cut at.
#:
#: Not quite the standard's 2 mm: molejo divides the loop by a whole
#: tooth count rather than stepping the nominal pitch around it, so a
#: loop this size comes out a fortieth of a percent short.  A real
#: pulley is cut at the nominal pitch and the machine takes the
#: difference up in belt tension; a drawing has no tension to take it
#: up with, so the pulley is cut to its own belt instead.
PERIOD = gt2.pitch(CIRCLES)

#: The upper run, the one the carriage's two clamps grip between them.
CLAMP_SPAN = 0

#: Where along the beam that run begins -- the tangent point on the
#: motor pulley -- which is what a carriage position is measured from to
#: reach the anchor.
CLAMP_ORIGIN = gt2.span_origin(CIRCLES, CLAMP_SPAN)[0]

#: Where on the pulley the belt leaves it, as an angle about the pulley's
#: centre: the tangent point the loop's own arc lengths are measured
#: from, and so the angle a tooth clamped at nought would stand at.
PULLEY_PHASE = math.atan2(
    gt2.span_origin(CIRCLES, CLAMP_SPAN)[1] - PULLEY[1],
    gt2.span_origin(CIRCLES, CLAMP_SPAN)[0] - PULLEY[0])


def pulley_angle(position):
    """Which way the motor pulley faces with the carriage at `position`.

    The pulley is not driven by the carriage on the machine -- it is
    the other way round, and the belt is what joins them -- but the
    belt is drawn from the carriage, so the angle that keeps a groove
    under every tooth is read from the carriage too.

    Two conversions and a division.  A carriage position becomes a
    length of belt the way `XBelt.clamp` does it, from the start of the
    clamped run and through that run's own tilt; that length becomes an
    angle at the pulley's pitch radius, subtracted because the loop
    runs clockwise, so a carriage moving along +X pays belt off the top
    of the pulley and turns it the same way; and the tangent point is
    where an anchor of nought puts a tooth.

    The loop's own length drops out of it.  It is a whole number of
    teeth by construction, so it is a whole number of the pulley's
    grooves too, and the pulley cannot tell one from another.

    Written as arithmetic rather than through `math.degrees`, because
    `position` is not always a number: the serialization pass drives
    the tree symbolically, and what comes through then is an expression
    in the machine's own `x` for the viewer to turn the pulley by.
    """
    anchor = (position - CLAMP_ORIGIN) * gt2.span_scale(CIRCLES, CLAMP_SPAN)
    turn = PULLEY_PHASE - anchor / (PULLEY_RADIUS + gt2.PITCH_LINE)
    return turn * 180 / math.pi


class XBelt(gt2.Belt):
    """The GT2 loop from the motor pulley at the left of the beam to the
    idler bearing at the right, clamped to the carriage in between.

    The loop stands still: both ends of it are bolted to the beam, and
    nothing about where the carriage is changes where the belt goes.
    What the carriage moves is the belt's *material* -- the teeth it
    grips travel with it, which is why the loop is drawn afresh at every
    position instead of being placed like a rigid part.

    `clamp` is where along the upper run the carriage holds the belt.
    The design puts two clamps on the carriage, one either side of its
    centre, and the belt is continuous between them, so the single
    number the loop needs is the carriage's own centre.
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
