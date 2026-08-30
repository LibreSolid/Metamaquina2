"""The GT2 timing belt both driven axes run, and the pulley it meshes on.

The OpenSCAD design draws a belt as a 2 mm thick ring hulled around the
things it wraps.  That is enough to see where the loop goes, and all a
still drawing needs, but it is not a belt: it has no teeth, and it does
not move.  A real belt has both, and the two are the same fact -- the
teeth are what the carriage is clamped to, so when the carriage travels
the teeth travel with it, through a loop that itself stands still.  That
is a shape to be re-drawn at every position rather than a solid to be
moved, which is what a flexible leaf is for.

This module holds what the two belts share, and what the pulley one of
them meshes on shares with it: what GT2 *is*.  The numbers here are the
belt standard's, because the design has none -- it never drew a tooth,
and its `GT2_pulley` module is an empty stub with a bill-of-materials
line and a `//TODO: implement-me!` inside it.  The design's own numbers
stay in `params` and arrive as arguments: which circles a belt runs,
how wide it is, and which radius it was drawn around.

molejo authors a belt as a `Wrap`: an ordered list of circles in the XY
plane, run along their external tangents, clockwise seen from +Z, with
the belt's width along +Z and the swept path being the belt's *pitch
line*.  Three consequences shape everything below.

* The circles a wrap takes are pitch circles, so a contact radius read
  off the design has to be converted -- and the conversion differs
  between a toothed pulley, whose grooves swallow the teeth, and a plain
  bearing, which the tooth tips ride on.  Hence `on_pulley` and
  `on_idler` rather than one function.
* The circles must be ordered clockwise.  The design lists the Y belt's
  three idlers the other way round, so that node lists them reversed:
  the same loop, run the way molejo runs it.
* A belt clamped to a carriage is anchored at a distance *along* one
  tangent span, while a carriage is at a position along the machine's
  axis.  Converting between the two needs to know where the span starts
  and how it is tilted.  molejo computes both internally and publishes
  neither, so `span_origin` and `span_scale` below restate its
  external-tangent rule.
* The tooth form is likewise molejo's, published only as the displaced
  mesh it draws, and a pulley the belt meshes on has to be that form's
  exact negative -- so `modulation` restates it too.  Those two
  restatements are the pieces of this module that would rather live in
  molejo.

Why the belts were done now
---------------------------

This branch exists to put solid-node's new flexible leaf in front of a
real machine rather than a sample one, and to say honestly what happened.

What worked: both belts are `MolejoNode` leaves under the axis that
drives them; each declares one port, the clamp its ends are held by, and
the axis wires that port from the same carriage position it places the
carriage with.  The teeth follow the carriage exactly -- a whole tooth of
travel redraws the belt identically, half a tooth moves a crest to a root
and not a micron further -- and both loops come out watertight, and exact
as OCCT solids to the tolerance molejo declares for a tooth ramp crossing
an arc.  They serialize as shapes rather than meshes, so whatever opens
the model redraws them itself.

What it cost, and what it found:

* A belt with teeth is drawn at the radius it really rides at, and that
  turned up a millimetre of nonsense the hulled ring had hidden: the
  design writes the Y loop's height down as a literal 66 while placing
  the bearings it runs on from `base_bars_height + base_bars_Zdistance`,
  which is 67.  The node derives it; see `y_axis.YAxis`.
* The interference assertion the framework offers cannot be used on a
  belt.  `assertNotIntersecting` takes an exact path only when both
  parts are exact, and every part of this machine but the belts is
  OpenSCAD; the mesh path it falls back to reaches for a cached STL,
  which a flexible part does not have and never writes.  It raises
  `FileNotFoundError` -- or, worse, quietly answers from the stale
  artifact a rigid part of the same name left behind, which is exactly
  what happened here first.  `assertRidesOn` in the test module takes
  the boolean itself and says why.
* A wrap's tessellation is spent per element, and a wrap has two
  elements per circle, so the 19 mm of arc at the end of the X beam is
  sampled as finely as the 375 mm run that carries 190 teeth.  See
  `PATH_SAMPLES`.

And what the pulley then found
------------------------------

The X belt is drawn meshed on a pulley, so the pulley had to become a
part rather than a radius, and asking which pulley it is turned up
three more things the stub had hidden.

* `PulleyRadius` is 6, and 6 is not a GT2 pulley.  A belt meshed on it
  wraps a pitch circle of 6.254, which carries 19.66 teeth -- and a
  pulley has a whole number of them or it does not mesh.  The whole
  number nearest what the design drew is 20, whose flanks stand at
  6.111, so the belt is drawn 0.111 mm further out at the motor end
  than the round number said.  See `pulley_teeth`, and
  `x_stage.x_belt.PULLEY_RADIUS` for the loop that closes on it.
* Both pulleys are placed somewhere their belt is not.  The X one is
  put one `thickness` off the plate it hangs behind, 6 mm out of the
  plane its own belt runs in; the Y one is left at the origin of the
  motor's assembly, 72 mm off the shaft.  Nothing showed while
  `GT2_pulley` drew nothing.  Both are placed from the belt instead;
  see `x_stage.ends.motor.belt_side` and `y_axis.motor.y_motor`.
* A trapezoidal tooth cannot get out of a trapezoidal groove, so a
  pulley drawn as the exact negative of its belt bites it at the two
  places where a tooth is halfway through.  A groove is the shape of
  everything a tooth does on its way in and out, which is `groove`,
  and which is what the curved grooves of a real timing pulley are.

Everything left after that is microns, and it is not chased.  Two
surfaces meeting exactly is a precision neither a moulded belt nor a
machined pulley has, and one a mesh boolean cannot even be asked about,
so the pulley is cut a tenth of a millimetre inside the belt all round
-- about the backlash such a pair really runs with, and well inside
what the rubber takes up by flexing.  See
`hardware.gt2_pulley.GT2Pulley.CLEARANCE`.

The one micron that is chased is the pulley's own pitch, which is cut
to the belt's rather than to the standard's.  Not for clearance, which
would swallow it, but because a tooth of belt is one groove of pulley
only when the two circles are the same circle, and a drive ratio ought
not to have a number in it that nothing chose.

The Y motor gets the same part and no mesh: the loop the design draws
runs on three bare bearings and never reaches the motor, so there is
nothing for those teeth to engage and nothing to derive an angle from.
"""

import math

import numpy
from molejo import Polygon, Teeth
from solid_node.node import MolejoNode

from metamaquina2 import materials
from metamaquina2.scad import scad_sources


#: The pitch of GT2, and what the standard is named after.
PITCH = 2.0

#: How far a tooth stands proud of the land between two teeth.
TOOTH_HEIGHT = 0.75

#: The belt's whole section, back and tooth together.
THICKNESS = 1.38

#: The pitch line differential: how far the pitch line -- the neutral
#: line a belt's length is measured along, and the line molejo sweeps
#: the section along -- lies outside the land between two teeth.  It is
#: what makes a 20 tooth pulley 12.32 mm across the flanks and 12.73 mm
#: across the pitch circle.
PITCH_LINE = 0.254

#: The back of the belt, from the pitch line outwards.
BACK = THICKNESS - TOOTH_HEIGHT - PITCH_LINE

#: How many rings molejo spends on each element of a loop.
#:
#: A wrap's tessellation is per element and a wrap has two elements per
#: circle -- one tangent span and one arc -- so every element gets this
#: many rings whether it is the 375 mm run down the X beam or the 19 mm
#: of arc at the end of it.  The long run is what sets the number: it
#: carries around 190 teeth, and a trapezoid needs several samples
#: across to read as a trapezoid rather than as noise.  A thousand is
#: the compromise this design is drawn at -- five or six rings a tooth
#: on the longest element, generous everywhere else -- and it is a
#: sampling instruction only: the exact solid and the loop's own
#: measurements are analytic and do not depend on it.
PATH_SAMPLES = 1024


def section(width):
    """The belt's cross-section, as molejo takes it.

    In a wrap's profile frame local x is the outward normal and local y
    is the world +Z the belt's width runs along, so this is the belt
    seen end-on with its teeth to the left.  The points run
    counter-clockwise, which is molejo's winding, and the two at the
    minimum x are the inner face `Teeth` displaces into teeth.

    The width runs from nought to `width` rather than either side of
    nought, so that a node placing this loop places it exactly where the
    design's own ``linear_extrude(belt_width)`` put its hulled ring.
    """
    return Polygon([
        (-PITCH_LINE, 0.0),
        (BACK, 0.0),
        (BACK, width),
        (-PITCH_LINE, width),
    ])


def on_pulley(centre, radius):
    """The pitch circle of a belt meshed on a toothed pulley.

    The pulley's teeth stand in the gaps between the belt's, so what
    touches the pulley's flank circle is the land between two teeth, and
    the pitch line is one pitch line differential outside it.
    """
    return {'center': [centre[0], centre[1]], 'radius': radius + PITCH_LINE}


def on_idler(centre, radius):
    """The pitch circle of a belt running teeth-down on a plain bearing.

    Both machines' idlers are 608 bearings with nothing to mesh with, so
    the belt rides them on its tooth *tips* -- a whole tooth further out
    than it sits on a pulley.
    """
    return {'center': [centre[0], centre[1]],
            'radius': radius + TOOTH_HEIGHT + PITCH_LINE}


def pulley_teeth(radius):
    """How many teeth a pulley whose flanks stand at `radius` carries.

    `tooth_count` read the other way, for a circle instead of a loop: a
    pulley's flank circle is one pitch line differential inside the
    pitch circle the belt runs on, and that circle carries a whole
    number of nominal pitches.  A design that writes a pulley down as a
    radius rather than as a tooth count -- as this one does, in
    `PulleyRadius` -- has named it by the wrong number, and this is
    which pulley it named.
    """
    return round(2 * math.pi * (radius + PITCH_LINE) / PITCH)


def pulley_radius(teeth, period=PITCH):
    """Where the flanks of a pulley of `teeth` teeth stand.

    `period` is the pitch its grooves are really spaced at, which for a
    pulley meshed with a drawn loop is the loop's own `pitch` and not
    the nominal `PITCH` a catalogue pulley is cut at: molejo divides a
    loop's length by a whole tooth count rather than stepping 2 mm
    around it, so a drawn loop comes out a fortieth of a percent off
    the standard.  On the machine that difference is taken up in belt
    tension.  In a drawing there is no tension to take it up with, so
    the pulley is cut to the belt it drives instead.
    """
    return teeth * period / (2 * math.pi) - PITCH_LINE


def modulation(fraction):
    """How much tooth stands at `fraction` of the way through one
    period: nought on the land between two teeth, one at a crest.

    molejo's own tooth form, restated -- a quarter crest centred on the
    pattern origin, a quarter ramp, a quarter root and a quarter ramp
    back.  molejo publishes it only as the mesh it displaces, and a
    pulley the belt meshes on is exactly this curve read as a solid's
    boundary rather than as an offset, so the two cannot be allowed to
    disagree.
    """
    fraction %= 1.0
    away = min(fraction, 1.0 - fraction)
    return max(0.0, min(1.0, (0.375 - away) * 4.0))


#: How finely a tooth's way out of its groove is followed.
#:
#: The sampling is square: this many stations across one tooth, and
#: this many advances for each of them, so a millionth of a tooth's
#: passage is looked at.  It is deliberately far finer than the outline
#: it feeds, which takes the deepest of a whole step at a time -- a
#: missed sample can only ever leave a groove tighter than it should be,
#: and the step is where that is made safe rather than here.
PASSAGE_SAMPLES = 1024

#: How far past the pitch circle a tooth is followed, in teeth.
#:
#: A crest sits 1.004 mm inside the pitch line, so it has cleared the
#: flank circle once it is 2.93 mm along the straight run -- a tooth and
#: a half.  Three is that with room, and the sampling stops early
#: anyway: `_passage` drops every station the moment its tooth is out.
PASSAGE_REACH = 3


def _passage(teeth, period, bins):
    """The deepest a tooth reaches into a pulley, by angle, on its way
    out of the groove it was seated in.

    A belt leaves a pulley along a tangent, so in the pulley's own frame
    a tooth on the way out is a tooth on a straight line rolling off a
    circle: it lifts out of its groove while the pulley turns under it,
    and it sweeps.  Everything here follows from that one picture.  A
    tooth seated at station `m` sits at pulley angle `m / pitch radius`
    and stays there; once it is `run` past the tangent point it stands
    at `hypot(seat, run)` from the centre, at an angle the pulley's own
    turn has carried a further `run / pitch radius` on and the tangent
    has swung `atan2(run, seat)` back.

    A groove is cut once and every tooth goes through it, so the answer
    is the deepest reach at each angle over the whole passage.  Coming
    on is going off with time reversed, which is a reflection, so the
    two halves are folded together at the end rather than derived
    twice.
    """
    pitch_radius = teeth * period / (2 * math.pi)
    flank = pitch_radius - PITCH_LINE

    station = numpy.linspace(0.0, period, PASSAGE_SAMPLES, endpoint=False)
    seat = pitch_radius - numpy.array(
        [PITCH_LINE + TOOTH_HEIGHT * modulation(place / period)
         for place in station])
    run = numpy.linspace(0.0, PASSAGE_REACH * period, PASSAGE_SAMPLES)[1:]

    radius = numpy.hypot(seat[:, None], run[None, :])
    angle = (station[:, None] / pitch_radius
             + run[None, :] / pitch_radius
             - numpy.arctan2(run[None, :], seat[:, None]))

    biting = radius < flank
    tooth = 2 * math.pi / teeth
    index = ((angle % tooth) / tooth * bins).astype(int) % bins

    deepest = numpy.zeros(bins)
    numpy.maximum.at(deepest, index[biting], (flank - radius)[biting])
    return numpy.maximum(deepest, deepest[(-numpy.arange(bins)) % bins])


def groove(teeth, period, steps, fine=16):
    """How deep a pulley's groove is at each of `steps` points through
    one tooth.

    Not the tooth's own shape.  A tooth is a trapezoid and a trapezoid
    cannot get out of a trapezoid: seat one exactly and it is trapped,
    because leaving means swinging about the tangent point and the
    corners have nowhere to swing to.  Drawn as the exact negative the
    pulley bites its own belt at the two places where a tooth is
    halfway in or halfway out -- two tenths of a cubic millimetre of
    it, at the two ends of the wrap and nowhere else, which is what
    sent this function looking.  So a groove is not the shape of a
    tooth; it is the shape of everything the tooth does on its way
    through, and the floor and the flat between two grooves come out
    untouched while the flanks are scooped back by up to 0.17 mm.
    That is what a real timing pulley's curved grooves are for.

    Each returned point is the deepest reach anywhere within one step
    either side of it, because a chord of the polygon this feeds stands
    as far out as its outer end: a tooth passing between two points has
    to clear both of them.  The over-cut that follows is flank
    clearance, which is a thing a pulley has and a drawing usually
    forgets, and it leaves the two surfaces that actually carry -- the
    groove floor and the land between grooves -- exactly where they
    were.
    """
    bins = steps * fine
    needed = numpy.maximum(
        _passage(teeth, period, bins),
        [TOOTH_HEIGHT * modulation(index / bins) for index in range(bins)])
    return [max(needed[(step * fine + offset) % bins]
                for offset in range(-fine, fine + 1))
            for step in range(steps)]


def tooth_count(circles):
    """How many teeth the loop through `circles` carries.

    molejo takes the count as a declaration rather than deriving it,
    because a count that followed a parameter would change the vertex
    count with it.  So it is derived once, here, from the loop the
    geometry gives: the nearest whole number of nominal pitches around
    it.  A belt is bought by tooth count and tensioned to fit, which is
    the same arithmetic run the other way.
    """
    return round(length(circles) / PITCH)


def pitch(circles):
    """The pitch the teeth of the loop through `circles` are drawn at.

    Not quite `PITCH`.  molejo divides the loop by the declared tooth
    count rather than stepping a nominal pitch around it, because a
    whole number of teeth is what closes the pattern at the seam and
    what keeps a moving idler changing the pitch rather than the count.
    A real belt does the same thing with its own tension.
    """
    return length(circles) / tooth_count(circles)


def teeth(circles):
    """The tooth pattern of a GT2 belt run around `circles`."""
    return Teeth(pitch=PITCH, height=TOOTH_HEIGHT, flank='trapezoid',
                 count=tooth_count(circles))


def length(circles):
    """The pitch length of the loop through `circles`.

    What a catalogue calls the belt's length, and what molejo divides by
    the tooth count to get the pitch it actually draws at.
    """
    return sum(span[2] for span in spans(circles)) + sum(_arcs(circles))


def span_origin(circles, span):
    """Where tangent span `span` of the loop begins, in the wrap's plane.

    The wrap's arc-length origin is where the belt leaves the first
    circle, and an anchor is measured from the start of the span it
    names, so this is the point a clamp's position is measured from.
    """
    return spans(circles)[span][0]


def span_scale(circles, span):
    """Millimetres of belt per millimetre of travel along tangent span
    `span`, for a carriage running along the wrap plane's x.

    An anchor is a distance along the span; a carriage is at a position
    along the machine's axis.  The two differ by the span's tilt, which
    is nought only when the two circles the span joins have the same
    radius -- as the Y belt's three do, and the X belt's pulley and
    idler do not.  On the X belt it comes to two parts in a million,
    well under a micron across the travel, so this is a correctness
    matter rather than a visible one.  It is written down because the
    conversion is real, not because the number is large.
    """
    return 1.0 / spans(circles)[span][1][0]


def spans(circles):
    """The loop's tangent spans, each as (start, direction, length).

    molejo's rule, restated: for consecutive circles at distance *L*
    with radii *r* and *r'*, the outward normal both are touched along
    is ``n = d*u + sqrt(1 - d*d)*rot90(u)`` for ``d = (r - r')/L`` and
    ``u`` the unit vector between the centres, and the belt runs from
    one tangent point to the next in the direction ``(n_y, -n_x)``.
    """
    normals = _normals(circles)
    result = []
    for index, normal in enumerate(normals):
        following = (index + 1) % len(circles)
        start = _touch(circles[index], normal)
        end = _touch(circles[following], normal)
        result.append((start, (normal[1], -normal[0]),
                       math.hypot(end[0] - start[0], end[1] - start[1])))
    return result


def _arcs(circles):
    """How much belt is wrapped around each circle, in order.

    The belt arrives on the normal of the span before a circle and
    leaves on the normal of the span after it, and turns clockwise
    between the two.
    """
    normals = _normals(circles)
    lengths = []
    for index in range(len(circles)):
        following = (index + 1) % len(circles)
        arrival = math.atan2(normals[index][1], normals[index][0])
        departure = math.atan2(normals[following][1], normals[following][0])
        turn = (arrival - departure) % (2 * math.pi)
        lengths.append(circles[following]['radius'] * turn)
    return lengths


def _normals(circles):
    """The outward normal the belt touches each circle on, in order."""
    normals = []
    for index in range(len(circles)):
        following = (index + 1) % len(circles)
        here, there = circles[index], circles[following]
        between = (there['center'][0] - here['center'][0],
                   there['center'][1] - here['center'][1])
        distance = math.hypot(*between)
        unit = (between[0] / distance, between[1] / distance)
        delta = (here['radius'] - there['radius']) / distance
        sideways = math.sqrt(1.0 - delta * delta)
        normals.append((delta * unit[0] - sideways * unit[1],
                        delta * unit[1] + sideways * unit[0]))
    return normals


def _touch(circle, normal):
    """Where a belt running on `normal` touches `circle`."""
    return (circle['center'][0] + circle['radius'] * normal[0],
            circle['center'][1] + circle['radius'] * normal[1])


class Belt(MolejoNode):
    """A GT2 belt of this machine, as a flexible leaf.

    Shares with `ScadPart` the thing every part in this package shares
    -- its dimensions are read from the .scad sources, which no Python
    import mentions, so an edit there has to invalidate it -- but not
    its geometry, which is molejo's rather than an OpenSCAD module's.

    A subclass declares one port per shape parameter and returns the
    shape; the axis that owns it connects the port.  Both belts here
    have exactly one parameter, the clamp their ends are held by.
    """

    color = materials.RUBBER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()
