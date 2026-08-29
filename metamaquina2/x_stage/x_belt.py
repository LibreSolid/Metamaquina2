"""The X axis belt."""

from molejo import P, Shape, Wrap
from solid_node.node import TranslationalPort

from metamaquina2 import gt2
from metamaquina2.params import (
    IdlerRadius,
    PulleyRadius,
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
    gt2.on_pulley(PULLEY, PulleyRadius),
    gt2.on_idler(IDLER, IdlerRadius),
]

#: The upper run, the one the carriage's two clamps grip between them.
CLAMP_SPAN = 0

#: Where along the beam that run begins -- the tangent point on the
#: motor pulley -- which is what a carriage position is measured from to
#: reach the anchor.
CLAMP_ORIGIN = gt2.span_origin(CIRCLES, CLAMP_SPAN)[0]


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
