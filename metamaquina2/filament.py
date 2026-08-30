"""The stock this machine eats, from the reel to where it goes in.

The design says what the filament is three times and draws it nowhere.
``FilamentSpoolHolder.scad`` declares ``diameter=3`` on a line of its
own and uses it in nothing; ``PTFE_liner.scad`` bores its liner ``d4 =
3.0`` and calls it "the filament runs down this"; and
``extruder_slice()`` cuts a 3.2 mm channel up the middle slice of the
extruder for it to arrive by.  What stands beside the machine is a
plain ABS tube, and between that tube and the extruder there is
nothing at all.

Filament is the third thing here whose shape is a function of where the
machine is, and it is the one the other two are not.  A belt's loop
stands still while the rubber inside it travels; a spring is shorter
when you press on it; the run from the reel to the extruder is a length
of stock hanging between a stand that never moves and a print head that
moves in X and in Z, so its shape at any instant is a function of both.
That is the case a sampled representation could only serve with a grid
over two axes, and the one molejo's own filament loom exists for.

What the layer is
-----------------

The design's reel is 160 mm of wound stock drawn as the cylinder it
comes to, which is honest for two hundred turns in four layers and no
use at all once the strand is a strand.  So the outermost layer is
drawn as the strand it really is and `spool` draws the tube to what is
wound under it: the layer's centre line runs half a stock inside the
design's own reel diameter, the tube stops a whole stock short of it,
and the two together still come to the 160 the design draws.

Nothing about the layer is chosen.  Its pitch is the stock's own
diameter, because the next turn of a wound reel lies against the last
one and there is no other pitch to have; its turn count is the most
whole turns of that which fit across the reel's width.  Fifty-two turns
of 3 mm rise 156 and take up 159 of the reel's 160 -- a helix occupies
its own rise plus one stock, half of it standing proud at each end,
which is the same millimetre `spring.rise` is about -- and the half
millimetre left over at each end is the width not dividing.

Whole turns matter twice.  A molejo helix begins at the point the path
has reached and winds about the tangent it arrived on, so a sweep of a
whole number of turns ends at the same angular position it started at
-- which is what lets `PLACEMENT` put both the reel's axis and the
place the strand leaves it where they belong at once.  And it is what a
reel does: a layer that ended on a fraction of a turn would be a reel
somebody had stopped winding mid-turn.

What is not drawn here
----------------------

Only one layer.  A helix winds about its incoming tangent, so a second
one chained after the first starts on the first's own pitch angle and
does not come out coaxial with it: a full reel is not one sweep, and
one layer is what a reel's surface is anyway.

And no gap under the layer, which has a consequence worth stating.  A
layer lies on what is wound beneath it -- that is what a wound reel is
-- so the drawn one is tangent to the drawn tube along its whole
twenty-six metres, and a swept helix is drawn as chords between its
rings.  Between one ring and the next the strand's surface therefore
falls `RADIUS * (1 - cos(180 / RINGS_PER_TURN))` inside the circle it
really runs on, about three tenths of a millimetre, and shares that
much with the tube everywhere at once.  Nothing here is misplaced --
the rings are on the true helix and reach the tube's own surface
exactly, which is what the contract asks -- and the alternative would
be to invent a clearance between a reel and the filament on it, or to
let a tessellation decide a diameter.

How the run goes
----------------

The stand is beside the machine and the extruder is inside it, so the
run cannot go straight there: the frame's right-hand side panel is a
wall of sheet from the floor to the frame's own height, and on the way
in there are the beam's own plate and the box at its end.  So the run
climbs from the reel to a crossing over the machine's own edge, travels
in from there at that height until it is over the extruder, and turns
down into the channel through the opening the top panel is cut with for
the carriage to travel in.

Three pinned points, and only two of them are numbers of their own:
where the run crosses, where it turns down, and where it ends.  The
turn is directly over the end at the height of the crossing, so it is
made of the other two and asks for no port at all.  `metamaquina2`
holds both, because what they are made of is the frame's own width and
how high the machine's own head ever gets, and both are the machine's.

Turning down over the extruder rather than curving straight at it is
not decoration.  A run pinned only at the crossing has to be vertical
by the time it reaches the channel, so it leaves the crossing already
falling and reaches the frame's right-hand side panel below the top
panel it was supposed to come down through -- which is what it did, at
the bottom of the Z travel with the carriage on the reel's side of the
machine.  Level until it is over the opening, and then down, is the
route that does not depend on how a spline happens to sag.

And the run stops at the mouth of the extruder's channel, which is a
finding rather than a preference: `metamaquina2` records the four
things the drawn machine has at and below that mouth, and the contracts
ask for all four.
"""

from molejo import Circle, Helix, P, Shape, Spline
from solid_node.node import MolejoNode, TranslationalPort

from metamaquina2 import materials
from metamaquina2.params import (
    filament_diameter,
    spool_diameter,
    spool_width,
)
from metamaquina2.scad import scad_sources


#: The radius the stock's centre line runs at on the reel.
#:
#: Half the design's own reel diameter, less half a stock: the design
#: measures its reel across the outside and molejo sweeps the section
#: along its centre line, so the layer drawn here reaches that diameter
#: rather than standing proud of it.
RADIUS = (spool_diameter - filament_diameter) / 2

#: How many turns of stock the outermost layer is: the most whole ones
#: that fit across the reel at the only pitch a layer has.
#:
#: One fewer than the width divides by, because a helix occupies its
#: own rise plus one stock diameter -- half a stock standing proud at
#: each end -- exactly as a spring occupies its helix plus one wire.
#: Fifty-two turns of 3 mm rise 156 and take up 159 of the reel's 160.
TURNS = int(spool_width / filament_diameter) - 1

#: How far the layer travels along the reel, which is those turns at
#: the stock's own diameter.  The stock itself takes up one diameter
#: more than this; `OFFSET` centres that on the reel rather than this.
TRAVERSE = TURNS * filament_diameter

#: How many rings of mesh each turn of the layer is drawn with.
#:
#: Thirty-six puts a ring every ten degrees, which on a reel of this
#: radius leaves the drawn surface three tenths of a millimetre inside
#: the circle between one ring and the next -- a tenth of the stock's
#: own diameter, and so fine enough that the layer reads as round
#: against the tube it lies on.  The springs state theirs per turn for
#: the same reason: a helix gets one tessellation for the whole sweep,
#: so a count per turn is the only one that means anything.
RINGS_PER_TURN = 36

#: What the document declares, which molejo spends on EACH element of
#: the path rather than dividing between them, and a spline is one
#: element per point it runs to.  So each of the free run's three spans
#: is drawn with as many rings as the whole layer, a few tenths of a
#: millimetre apart.  That is the cost of chaining a dense primitive to
#: sparse ones in a format whose tessellation is fixed by the document,
#: and it is paid rather than worked around: splitting them into
#: separate parts to spend less would draw a strand in four pieces.
PATH_SAMPLES = RINGS_PER_TURN * TURNS

#: How many points go round the stock.
#:
#: Eight, which puts the section's flats 0.114 mm inside the stock's
#: own circle -- about the tenth of a millimetre `jhead.FIT` calls the
#: smallest thing a drawing here resolves, and small against a 3 mm
#: strand seen at machine scale.  Sixteen, as the springs spend, would
#: be sixty thousand vertices redrawn at every position of two axes for
#: a difference no snapshot shows.
PROFILE_SAMPLES = 8

#: How the strand's own frame is turned onto the machine.
#:
#: A molejo path starts at the origin along +z and a helix winds about
#: the tangent it starts on, so the strand is authored with the reel's
#: axis as its own z, its start a radius out along +x, and the way it
#: is travelling as it comes round to the top as +y.  A third of a turn
#: about this diagonal is the one rotation that lands all three at
#: once: the axis down the reel's own, the radius up to the top of it,
#: and the direction of travel at the machine.
PLACEMENT = (120, [1, -1, 1])

#: Where the strand's own origin stands, from the centre of the reel.
#:
#: Half the traverse along the reel's axis, so the layer comes out
#: centred on the reel's width, and a layer radius up, because the
#: strand starts on the reel's surface rather than on its axis.  The
#: machine turns the stand to put the bar across it, so the axis is the
#: machine's y and this is read in the machine's own coordinates.
OFFSET = [0, TRAVERSE / 2, RADIUS]

#: Which way is down, read in the strand's own frame: what the free run
#: has to arrive along to be pointing down the extruder's channel.
DOWN = [-1, 0, 0]


def in_strand_frame(point, origin):
    """Read a point of the machine in the strand's own frame.

    `PLACEMENT` turns the strand's x onto the machine's z, its y onto
    the machine's -x and its z onto the machine's -y, so reading a
    machine point back is that permutation the other way round.  Only
    a reordering and three sign changes, which is what lets the machine
    hand these to the ports as expressions over its own drivers rather
    than as numbers.
    """
    x, y, z = (point[0] - origin[0],
               point[1] - origin[1],
               point[2] - origin[2])
    return [z, -x, -y]


class Filament(MolejoNode):
    """The loaded machine's filament: a layer on the reel and the run.

    One strand, not two parts: the turns lying on the reel and the free
    run to the extruder are the same length of stock, so they are one
    sweep -- a helix continued by a spline that leaves it the way it
    came, which is a joint with no kink in it and no literal tangent
    that could have said so.

    Its ports are the places the run is pinned, which are the only
    things about a length of stock that are not the stock: where it
    crosses the machine, and where it goes in.  The machine binds both,
    from the frame and the travel it owns and from where it puts its
    own extruder, so driving X or Z redraws the run and leaves the
    layer where it lies -- a reel does not turn when a print head
    moves.

    Five rather than six, because the two share their third coordinate:
    the run comes across the machine in the same plane it goes in on,
    so `plane` is one number and it is the same number twice.

    And the third pinned point -- where the run turns down, over the
    extruder at the height it came across at -- costs nothing at all,
    because it is the crossing's own height with the end's own two
    numbers.  Which is the whole of what a parametric shape buys: a
    point of the machine can be made out of ports already bound rather
    than declared again.

    Shares with `ScadPart` the thing every part in this package shares:
    its dimensions come from the .scad sources, which no Python import
    mentions, so an edit there has to invalidate it.  Not its geometry,
    which is molejo's.
    """

    color = materials.ABS

    over_x = TranslationalPort(unit='mm')
    over_y = TranslationalPort(unit='mm')
    head_x = TranslationalPort(unit='mm')
    head_y = TranslationalPort(unit='mm')
    plane = TranslationalPort(unit='mm')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()

    def render(self):
        return Shape(
            profile=Circle(radius=filament_diameter / 2),
            path=[
                Helix(radius=RADIUS, turns=TURNS, height=TRAVERSE),
                Spline(points=[[P.over_x, P.over_y, P.plane],
                               [P.over_x, P.head_y, P.plane],
                               [P.head_x, P.head_y, P.plane]],
                       end_tangent=DOWN),
            ],
            path_samples=PATH_SAMPLES,
            profile_samples=PROFILE_SAMPLES,
        )
