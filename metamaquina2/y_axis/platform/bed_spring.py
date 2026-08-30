"""The spring a corner of the heated bed stands on."""

from metamaquina2.params import (
    heatedbed_spring_length,
    m3_diameter,
    m3_washer_thickness,
    pcb_height,
    thickness,
    YPlatform_zoffset,
)
from metamaquina2.spring import Spring


#: The space between the top face of the platform sheet and the
#: underside of the bed board, taken from where this package puts those
#: two parts rather than from what the design calls the gap.
#:
#: The design states this one distance twice and disagrees with itself.
#: `pcb_height` is the platform deck plus the sheet plus
#: `heatedbed_spring_compressed_length`, with the deck taken from
#: `YPlatform_height` -- 84.7, the rods plus half a bearing.  But
#: `YPlatform_subassembly` stands that same deck at a literal `100-15`,
#: marked `/*TODO*/`, which is 85.  So the gap the two placed parts
#: leave is 7.1 mm and the variable that names it says 7.4.
#:
#: A spring drawn to 7.4 would hang three tenths of a millimetre above
#: the platform it is supposed to push off.  A spring is as long as the
#: room it is in, so the room is what it is drawn to, and the number
#: the design would rather it were is recorded here instead of being
#: used.
SEAT = pcb_height - (YPlatform_zoffset + thickness)

#: What is left of that once the washer under the bed board is in it.
INSTALLED = SEAT - m3_washer_thickness


class BedSpring(Spring):
    """One of the four springs the heated bed stands on.

    ``Compression Spring CM351 (D=4.5mm, lenght=15.3mm)``, four of
    them, from the block of parts `heated_bed()` buys and never draws.

    The free length is the design's own `heatedbed_spring_length`
    rather than the 15.3 of the catalogue line: the two disagree, the
    variable is the one the design does arithmetic with, and it is the
    smaller, so a contract that asks the spring to be installed shorter
    than free asks the harder of the two questions.

    Drawn standing on the platform's top face, at the origin of the
    levelling screw that runs through it.
    """

    coil_diameter = 4.5
    free_length = heatedbed_spring_length
    bore = m3_diameter
    installed = INSTALLED
