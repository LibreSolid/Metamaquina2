"""The brass nozzle: heater block, thread and orifice in one part."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import nozzle


class Nozzle(ScadPart):
    """The J-Head 0.35 mm nozzle, from the design's own module.

    `nozzle.scad` is `doc/Jhn_md_brass_heater_nozzle.jpg` already
    transcribed -- the 0.500" block, the 0.325" of height, the orifice
    at 0.020", the melt chamber, and the two holes the resistor and the
    thermistor go into -- and unlike `jhead.scad` it parses.  So it is
    called and not redrawn.

    Its origin is a corner of the heater block's base rather than the
    filament axis, which is at 0.15625" and 0.250" in from two of the
    block's faces; the hot end puts the axis where it belongs.  The
    offset is not decoration: it is what leaves room for the heater
    resistor to be drilled through beside the filament.

    One disagreement, recorded because it is between the design and its
    own drawing rather than anything this layer did.  The drawing says
    "Thread to 3/8-24" and gives 0.375" beside it; the module draws the
    stub at a radius of 0.15625", which is 5/16".  The holder's foot is
    tapped 3/8-24 as its own drawing says, so the drawn stub stands in
    the drawn hole with a quarter of a millimetre of slack instead of
    threading into it.  Correcting it would mean redrawing a part the
    design does draw, which is the one thing this layer does not do.
    """

    color = materials.GOLD

    def render(self):
        return nozzle.v4nozzle()
