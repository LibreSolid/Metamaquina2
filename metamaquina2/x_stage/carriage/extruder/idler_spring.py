"""The spring that presses the extruder idler onto the filament."""

from solid_node.node import Length

from metamaquina2.params import m4_diameter
from metamaquina2.spring import Spring


class IdlerSpring(Spring):
    """One of the two springs on the extruder handle's long bolts.

    ``Compresison Spring CM1678 (6mm x 16.5mm) - TODO:check this!``,
    two of them, from the block of parts `handle()` buys and never
    draws.  The design's own note is worth keeping: it was not sure of
    this line either.

    Unlike the bed's springs, this one is drawn at its free length.
    The design leaves 25 mm of shank between the idler's back plate and
    the bolt head and puts 17.25 mm of washer and spring in it, so the
    remaining 7.75 mm is not slack in the drawing -- it is the
    adjustment.  What takes it up is the lock nut the bill of materials
    buys and no module draws, which is what a maker turns to set how
    hard the idler grips.  The design states no setting, so the spring
    is drawn at the one length the design does state, and how far it is
    wound in is the port's business rather than this part's.
    """

    #: The catalogue's free length, kept as a bare number as well
    #: because the spring is both bought and drawn at it, and a
    #: declaration cannot be assigned under two names.
    FREE_LENGTH = 16.5

    coil_diameter = Length(6.0, min=0)
    free_length = Length(FREE_LENGTH, min=0)
    bore = Length(m4_diameter, min=0)

    #: Drawn free: the design gives the preload no number.
    installed = Length(FREE_LENGTH, min=0)
