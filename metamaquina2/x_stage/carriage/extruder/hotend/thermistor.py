"""The thermistor that tells the machine how hot the block is."""

from metamaquina2 import jhead, materials
from metamaquina2.part import ScadPart, curve


#: How thick the lead wire is, how far apart the two leads are, and how
#: far they run out of the block.
#:
#: Nominal, for the reason the resistor's leads are: the design buys the
#: part by reference and drills for it and says nothing else.  A glass
#: bead thermistor brings both leads out of the same end on fine wire,
#: which is what these are.
LEAD = 0.3
LEAD_GAP = 0.8
LEADS = 12


class Thermistor(ScadPart):
    """The TV100000X in the hole drilled for it, bead first.

    The design buys it under the same `//TODO: Add these parts to the
    CAD model` as the heater resistor, having drilled it a 0.090" hole
    0.170" into the side of the heater block, and the drawing that hole
    comes off says outright how to read it: "Use dimensions of
    thermistor to determine hole dimensions".  So the bead is the hole,
    less the slip fit in `jhead`.

    Standing on its own origin with the bead at the far end of the hole
    and the leads running back out along -Z, so an assembly points -Z
    at the face the hole is drilled into.
    """

    color = materials.GLASS

    def render(self):
        bead = curve(
            'cylinder', r=(jhead.THERMISTOR_DIAMETER - jhead.FIT) / 2,
            h=jhead.THERMISTOR_DEPTH,
        )

        wire = None
        for side in (-1, 1):
            lead = curve(
                'cylinder', r=LEAD / 2, h=LEADS,
            ).translate([side * LEAD_GAP / 2, 0, -LEADS])
            wire = lead if wire is None else wire + lead

        return bead + wire
