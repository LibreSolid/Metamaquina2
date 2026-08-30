"""The compression springs of this machine, as flexible leaves.

The design buys six of them and draws none.  Four hold the heated bed
up off the Y platform so that a nut at each corner can pull it down
until the bed is level; two ride the extruder handle's long bolts and
press the idler onto the filament.  Both live inside a block the design
heads ``//TODO: Add these parts to the CAD model``.

A spring is the part a flexible leaf is for, and more plainly than a
belt is.  A belt's shape follows the machine because the rubber inside
a standing loop travels; a spring's shape follows the machine because
the thing is shorter when you press on it.  There is no pose of the
machine at which one length of it is the right one, which is why the
length arrives through a port rather than being drawn into the part.

What the design gives, and what it does not
-------------------------------------------

The bill of materials names a spring the way a catalogue does: a
reference, an outside diameter and a free length.  ``Compression Spring
CM351 (D=4.5mm, lenght=15.3mm)``, and the extruder's ``CM1678 (6mm x
16.5mm)``.  Nothing about the wire and nothing about how many turns
there are, and those are the two numbers a drawing needs.

So they are derived rather than chosen.  The wire is as thick as it can
be while the coil still runs clear on the shank threaded through it,
which is `BORE_CLEARANCE`; the turn count is as many as will fit while
consecutive coils still clear each other by a wire's own thickness at
the length the spring is installed at.  Both come out round for both
springs -- half a millimetre of wire in six turns under the bed, three
quarters in ten turns on the handle -- which is the sort of agreement a
derivation earns and a guess does not.  The tests ask the metal for
both.

What is not drawn here
----------------------

A real compression spring's end coils are pitched flat and ground
square, so the spring meets what it presses on across a whole coil
instead of at a point.  molejo sweeps one continuous helix and has no
vocabulary for closing an end, so these are drawn as bare helices.  The
consequence to keep in mind is dimensional rather than cosmetic: the
space a spring occupies is its helix plus one wire diameter, half a
wire standing proud at each end, which is what `rise` is about.
"""

from molejo import Circle, Helix, P, Shape
from solid_node.node import MolejoNode, TranslationalPort

from metamaquina2 import materials
from metamaquina2.scad import scad_sources


#: How much room a coil's bore is given over the shank it runs on.
#:
#: Half a millimetre on the diameter, a quarter all round.  A spring is
#: not a bearing: it is threaded loose over its bolt and it moves along
#: it, so this is a running fit rather than the tenth of a millimetre a
#: pulley is bored over its shaft with.  It is also the one free number
#: in the whole part -- everything else is the catalogue's or follows
#: from it -- and both springs land on a round wire size through it,
#: which is the argument for this figure rather than another.
BORE_CLEARANCE = 0.5

#: How many rings of mesh each turn of a helix is drawn with.
#:
#: A wrap gets its tessellation per element and a helix gets one for the
#: whole sweep, so a spring's is stated per turn instead and multiplied
#: up: a six turn spring and a ten turn one are then drawn to the same
#: fineness rather than to the same total.  Forty-eight puts a ring
#: every seven and a half degrees, which on a two millimetre coil is a
#: quarter of a millimetre of wire between rings -- finer than the wire
#: is thick, and so fine enough that the coil reads as round where it
#: sits against the flat it presses on.
RINGS_PER_TURN = 48

#: How many points go round the wire.
#:
#: Sixteen, the same count the framework's own example spends, which
#: puts the section's flats half a thousandth of a millimetre inside the
#: wire's circle.  That is what the seating tolerance in the tests is
#: measured against, and it is two orders under anything the contracts
#: here separate.
PROFILE_SAMPLES = 16


def wire(diameter, bore):
    """How thick the wire of a spring of `diameter` over `bore` is.

    The catalogue's outside diameter, less the shank it has to run on,
    less the clearance it runs with, and half of that because the wire
    is on both sides of the bore.
    """
    return (diameter - bore - BORE_CLEARANCE) / 2


def turns(rise, wire_diameter):
    """How many turns fit in `rise` without the coils closing up.

    The most whole turns that still leave a clear wire diameter between
    consecutive coils.  A coil clearance of about the wire is the usual
    guideline for a spring that is not meant to reach solid in service,
    and here it is doing a second job: it is the only thing standing
    between a catalogue line that names no turn count and a drawing
    that would have to invent one.
    """
    return int(rise / (2 * wire_diameter))


class Spring(MolejoNode):
    """A compression spring, as the length it is installed at.

    A subclass states the three things the bill of materials knows --
    the outside diameter, the free length, and the shank the spring is
    threaded on -- plus the length the design installs it at, and
    everything else follows.

    Shares with `ScadPart` the thing every part in this package shares:
    its dimensions come from the .scad sources, which no Python import
    mentions, so an edit there has to invalidate it.  Not its geometry,
    which is molejo's.

    The port carries the helix's own rise, not the length the spring
    occupies, because that is what molejo's `Helix` takes and a
    parameter reference is a plain reference rather than an expression.
    The two differ by one wire diameter; `rise` is where the conversion
    is made and `installed` is the length a builder would measure.
    """

    color = materials.METAL

    #: What the bill of materials buys: the coil's outside diameter and
    #: its free length, both in millimetres.
    coil_diameter = None
    free_length = None

    #: The shank the spring is threaded on, which is what its bore has
    #: to clear.
    bore = None

    #: The length the design leaves the spring standing in.
    installed = None

    #: Published so a contract can ask the metal for the clearance the
    #: wire was derived from, rather than restating it.
    bore_clearance = BORE_CLEARANCE

    height = TranslationalPort(unit='mm')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()

    @property
    def wire_diameter(self):
        """How thick the wire is."""
        return wire(self.coil_diameter, self.bore)

    @property
    def coil_radius(self):
        """The radius the wire's centre runs at.

        Half the catalogue's outside diameter, less half a wire: the
        catalogue measures a spring across its outside and molejo sweeps
        the wire along its centre line.

        Also how far off its own origin the coil's axis stands.  A
        molejo path begins where the path has got to, which for a
        spring's single helix is the origin, so the wire starts there
        and the axis it winds about is a radius away in -x.  An
        assembly standing a spring on a bolt moves it out by this
        much.
        """
        return (self.coil_diameter - self.wire_diameter) / 2

    @property
    def rise(self):
        """The helix's own length at the installed length.

        Shorter than the space the spring occupies by one wire
        diameter, because half a wire stands proud below the first turn
        and half above the last.  An assembly that stands a spring on a
        face therefore lifts it half a wire and gets the whole length
        back.
        """
        return self.installed - self.wire_diameter

    @property
    def turns(self):
        """How many turns this spring is drawn with."""
        return turns(self.rise, self.wire_diameter)

    def render(self):
        return Shape(
            profile=Circle(radius=self.wire_diameter / 2),
            path=[Helix(radius=self.coil_radius,
                        turns=self.turns,
                        height=P.height)],
            path_samples=RINGS_PER_TURN * self.turns,
            profile_samples=PROFILE_SAMPLES,
        )
