"""What the Z screws do: turns into height, and height into turns.

The X stage does not float at a height somebody typed in.  It hangs on
two M8 nuts, each captive in a Z link, each threaded onto a bar that a
motor below it turns; the beam is where it is because the screws have
been turned that far, and it goes up because they go on turning.  This
module is that sentence as arithmetic, in one place, because four
others need it and none of them may reach a different answer: the
machine, which declares the driver; the bars and the couplings, which
turn; and both X ends, which carry a nut.

`SCALE` is the whole of it.  The Z driver's state is the screws' own
angle, in degrees, and `SCALE` is what a degree of it is worth in
millimetres of beam.  It is NEGATIVE, and that is the thread's
handedness rather than a convention: an M8 bar is right-handed, so a
nut that cannot turn climbs it when the bar is turned clockwise seen
from above, and clockwise from above is a negative rotation about Z.
So a machine standing at the top of its travel has had its
screws turned a hundred and twenty turns clockwise from where they
started, and its driver says so.

`PHASE` is the other half of the same fact, and it is what makes the
nut a nut rather than a ring hanging near a bar.  Both parts are drawn
with their thread crossing angle zero at their own base, because each
is drawn alone and knows nothing of the other; they are two different
distances up the machine, so their threads only line up if the bar is
turned by the difference between those distances, read as an angle.
That is what a builder does with the screws in their hands when the
stage goes on -- and, unlike the height, it does not change as the
machine moves, which is why it is a constant and not a term of the
lift.

`HOMING_RATE` is Marlin's own Z homing feedrate for a machine like this
one, 4 mm/s, which is 192 rpm at this lead.  Homing Z takes the time
that rate takes, and the time it takes is the point: this is a screw,
not a belt, and the interface should show a maker the difference.
"""

from metamaquina2.params import (
    BottomPanel_zoffset,
    BuildPlatform_height,
    BuildVolume_Z,
    ZLink_nut_seat,
    m8_nut_height,
    motor_shaft_length,
    nozzle_tip_distance,
    thickness,
)
from metamaquina2.thread import PITCH


#: How far one turn of a bar raises the beam.  An M8 bar is single
#: start, so its lead is its pitch and nothing else.
LEAD = PITCH

#: Millimetres of beam per degree of screw -- see the module docstring
#: for the sign.
SCALE = -LEAD / 360

#: Where a Z bar's foot stands, above the bottom panel by the length of
#: the motor shaft the coupling joins it to.
BAR_BASE = BottomPanel_zoffset + motor_shaft_length

#: Where a Z nut's own base sits inside its X end.  The ZLink's hex
#: socket opens at the bottom of the end and the captive plate closes
#: it `ZLink_nut_seat` up, so the nut hangs with its top face against
#: that plate: the plate is what the beam's weight comes down on.
NUT_SEAT = thickness + ZLink_nut_seat - m8_nut_height

#: Where that base stands on the machine when the beam is at nought.
NUT_BASE = BuildPlatform_height + nozzle_tip_distance + NUT_SEAT

#: How far the bars are turned from their own drawn phase to meet the
#: nuts -- see the module docstring.
PHASE = 360 * (BAR_BASE - NUT_BASE) / LEAD

#: What a Z axis homes at, in millimetres a second.
HOMING_RATE = 4.0

#: How long homing Z is allowed to take: the whole declared travel at
#: that rate, because an instruction states a duration and a machine
#: asked to home has no idea how far it has to go.
HOMING_TIME = BuildVolume_Z / HOMING_RATE


def angle(height):
    """The screws' angle, in degrees, that holds the beam at `height`."""
    return height / SCALE


def lift(turned):
    """The height, in millimetres, that screws `turned` that many
    degrees hold the beam at."""
    return turned * SCALE
