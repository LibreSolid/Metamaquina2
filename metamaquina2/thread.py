"""The ISO metric thread, drawn rather than named.

An M8 bar is not an 8 mm cylinder.  The design draws it as one --
``cylinder(r=m8_diameter/2)``, everywhere a bar appears -- and for a
bar that only stiffens a frame that is a fair drawing: nothing about
the machine depends on where its crests are.  The two bars of the Z
axis are the exception, and they are the exception that matters.  Those
are what holds the X stage up.  A nut on a plain cylinder is a nut
around a pole: it does not hang on anything, it cannot be lifted by
turning the pole, and the model has no way to be wrong about either,
because there is nothing there to be wrong with.

So the thread is here, as geometry.  It is the ISO basic profile: a
60 degree V of height ``H = P*sqrt(3)/2``, truncated flat at ``P/8``
across the crest and ``P/6`` across the root, which puts the crest on
the major diameter and the root on ``d3 = d - 2*(17/24)H`` -- the same
numbers a table of M8 coarse gives.  A bar is that V wound up a helix
of one pitch per turn, over a core cylinder at the root radius.

Two decisions are worth knowing about before reading the code.

The thread is swept in SEGMENTS rather than as one helix from end to
end.  It is not a subdivision for its own sake: OCCT's pipe sweep
drifts over a long spine, and a single 230 turn sweep of a Z bar comes
back with the volume of no solid at all -- negative, in fact.  Segments
of `TURNS_PER_SEGMENT` come back exact, and they fuse into the core as
one bar.

`CLEARANCE` is a drawing decision and not a fit.  A nut is cut by this
same profile GROWN by it, so nut and bar come from one authority and
cannot be given two different thread forms by accident -- and what the
number may be is decided by the root flat, not by taste.  Growing the
profile pushes both flanks into the ``P/6`` groove between two turns,
and that groove is what is left over as the NUT's own crest: at
``P/12 * cos 30`` of clearance -- ninety micron here -- there is no
crest left and the nut has no thread at all.  Forty micron inside that
limit leaves the nut a tenth of a millimetre of land, gives the pair a
ninth of a millimetre of backlash, which is about what a commercial M8
nut on studding really has, and is orders above anything a boundary
kernel could mistake for contact.
"""

import math

from build123d import (Align, Box, Cylinder, Helix, Plane, Polygon, Pos,
                       sweep)


#: The coarse pitch of an M8 thread, in millimetres, and the lead of a
#: single-start bar: one turn, one pitch.
PITCH = 1.25

#: Half the included angle of the V, in degrees.  Everything the
#: profile does radially it also does axially, through this.
FLANK_ANGLE = 30

#: How far the crest is cut back from the sharp V, as a fraction of the
#: pitch.  The root's own flat is not declared beside it because it is
#: not free: the crest flat and the root radius fix it, and it comes out
#: at the ``P/6`` a thread table gives.
CREST_FLAT = 1 / 8

#: What a nut is cut with beyond the bar it runs on -- see the module
#: docstring for why it may not be much more.  Applied normal to every
#: face of the profile, so it is a flank clearance and a radial
#: clearance at once.
CLEARANCE = 0.05

#: How many turns one swept segment carries.  Small enough that OCCT's
#: sweep stays exact over it (see the module docstring), large enough
#: that a bar is a couple of dozen segments and not a couple of hundred:
#: measured against a Z bar, ten turns builds faster than five and is no
#: less exact, and twenty costs more in every boolean afterwards than it
#: saves in the fusing.
TURNS_PER_SEGMENT = 10

#: How far the rib reaches inside the core it stands on.  The two are
#: fused, and a rib that merely touched the core would ask the kernel
#: to decide a tangency; this gives it an overlap to cut into instead.
#: Small, because the flanks carry on down as they go: sink the rib far
#: and its section grows wider than the pitch, and then it sweeps
#: through its own previous turn.
SINK = 0.05


def height(pitch=PITCH):
    """The height of the sharp V the profile is truncated from."""
    return pitch * math.sqrt(3) / 2


def crest_radius(diameter=8.0):
    """Where an external thread's crests stand: the major diameter."""
    return diameter / 2


def root_radius(diameter=8.0, pitch=PITCH):
    """Where an external thread's roots stand.

    ``d3 = d - 2*(17/24)H`` -- the V truncated by ``P/6`` at the root,
    written the way a thread table writes it.
    """
    return diameter / 2 - (17 / 24) * height(pitch)


def thread(length, base=0.0, diameter=8.0, pitch=PITCH, clearance=0.0):
    """The solid of an ISO metric thread, from `base` to `base + length`.

    Phased so the helix crosses angle zero at ``z = 0``, whatever `base`
    is: that is what lets a nut and a bar be drawn independently and
    still mesh, because each carries the same thread of the same machine
    and the assembly says only where each one sits and how far the bar
    has been turned.

    The ends are cut flat, as a bar is cut flat, by sweeping a whole
    pitch past each of them and trimming.
    """
    tan_flank = math.tan(math.radians(FLANK_ANGLE))
    cos_flank = math.cos(math.radians(FLANK_ANGLE))
    crest = crest_radius(diameter) + clearance
    root = root_radius(diameter, pitch) + clearance
    inner = root - SINK

    def half_width(radius):
        """Half the rib's axial width where it stands at `radius`."""
        return (CREST_FLAT * pitch / 2 + (crest - radius) * tan_flank
                + clearance / cos_flank)

    # The rib in its own axial section, as (radius, axial offset): the
    # crest flat and a flank each side of it, carried `SINK` past the
    # root so the rib has something to cut into the core with.  The
    # root flat is what is left of the pitch between two of these, and
    # comes out at P/6 by construction.
    section = [(inner, -half_width(inner)),
               (crest, -half_width(crest)),
               (crest, half_width(crest)),
               (inner, half_width(inner))]

    # A whole pitch below the first cut and above the last, and started
    # on a multiple of the pitch so the phase above holds.
    start = math.floor(base / pitch) * pitch - pitch
    turns = math.ceil((base + length + pitch - start) / pitch)

    bar = Pos(0, 0, start) * Cylinder(
        radius=root, height=turns * pitch,
        align=(Align.CENTER, Align.CENTER, Align.MIN))

    for first in range(0, turns, TURNS_PER_SEGMENT):
        spine = Helix(pitch=pitch,
                      height=min(TURNS_PER_SEGMENT, turns - first) * pitch,
                      radius=crest,
                      center=(0, 0, start + first * pitch))
        plane = Plane(origin=spine @ 0, x_dir=(1, 0, 0), z_dir=spine % 0)
        rib = plane * Polygon(*[(radius - crest, offset)
                                for radius, offset in section], align=None)
        bar += sweep(rib, spine, is_frenet=True)

    return bar & (Pos(0, 0, base + length / 2)
                  * Box(4 * crest, 4 * crest, length))
