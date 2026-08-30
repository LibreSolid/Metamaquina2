"""The power resistor that heats the block."""

from metamaquina2 import jhead, materials
from metamaquina2.part import ScadPart, curve


#: How thick the lead wire is, and how far it stands out of each end.
#:
#: Nominal, and the only two numbers in this part that are.  The design
#: buys the resistor by reference and drills a hole for it and says
#: nothing else about it, so the body is the hole -- see the class --
#: and these are what a five watt wirewound resistor is really made
#: with: 0.8 mm tinned wire, cut long and bent to reach the wiring.
LEAD = 0.8
LEADS = 12


class HeaterResistor(ScadPart):
    """The UB5C-5RF1 the bill of materials buys, on its own axis.

    Drawn here because the design draws nothing: `v4nozzle` buys it
    inside a block headed `//TODO: Add these parts to the CAD model`,
    having already drilled the 0.234" hole that goes right through the
    heater block for it.

    So the hole is the part.  The drawing beside it says as much about
    the thermistor -- "Use dimensions of thermistor to determine hole
    dimensions" -- and the same reading is the honest one here: the
    body is what the design drilled for, less the slip fit in `jhead`,
    and its length is the block it passes through.  Nothing about a
    five watt resistor's real body length is stated anywhere in this
    repository, so nothing about it is claimed.

    Standing on its own axis with the body centred on the origin, so an
    assembly puts it on the axis of the hole and does not have to know
    which end is which.  One colour, like every leaf here, and it is
    the ceramic's: the leads are drawn because a resistor with no leads
    could not be wired, not because the palette has anything to say
    about them.
    """

    color = materials.CERAMIC

    def render(self):
        radius = (jhead.HEATER_DIAMETER - jhead.FIT) / 2
        body = curve(
            'cylinder', r=radius, h=jhead.BLOCK,
        ).translate([0, 0, -jhead.BLOCK / 2])

        leads = curve(
            'cylinder', r=LEAD / 2, h=jhead.BLOCK + 2 * LEADS,
        ).translate([0, 0, -jhead.BLOCK / 2 - LEADS])

        return body + leads
