"""The Metamaquina 2, as an assembly.

The machine is designed in OpenSCAD, in the .scad files beside this
package, and that design is left exactly as it is.  What this package
adds is a second reading of it: a tree of nodes in which every part a
builder handles -- every plate that gets cut, every bolt that gets
turned, every bearing that gets pressed -- is a leaf, and every group
that gets put together before it goes into something bigger is an
assembly.

The tree follows the build, not the source file.  A frame first,
because nothing can be fitted until the panels and bars are square.
Then the three axes, each with its own rods, its own drive, and the
thing it moves.  Then the electronics, which go on last.  The spool
holder is a separate stand and hangs off the root beside the machine,
which is where the design draws it.

The design already had a knob for each axis -- `XCarPosition`,
`YCarPosition` and `ZCarPosition`, the three numbers that decide where
the .scad file draws a machine at rest.  Here they are drivers instead:
the same coordinates, with the same numbers as defaults, but read at
every render rather than baked in once.  So the machine that opens is
the machine that has always been drawn, and it can now be sent
somewhere else without editing anything.

What moves is what carries the print: the carriage along the X beam,
the bed along its rods, the whole X beam up and down the Z rods.  Two
things turn with them.  One is the pulley the X belt is meshed on,
because a groove has to stay under every tooth that comes round to it
and the belt says exactly where.  The other is the pair of Z screws,
and they are not decoration: the beam does not float at a height
somebody typed in, it hangs on two M8 nuts that a right-handed thread
lifts a millimetre and a quarter per turn.  So Z is the one axis whose
driver is not a position at all -- it is the screws' own angle, and the
height is what that angle is worth.  `z_screw` holds the arithmetic,
`thread` draws the form both the bars and their nuts are cut from, and
the couplings under the bars go round with them because that is what a
coupling clamped to a shaft does.

The two belts used to stand still for a different and worse reason.  A
belt does not go anywhere: both ends of each loop are bolted down, and
the loop keeps its shape from one end of the travel to the other.  But
it is not still either -- the rubber inside the loop is dragged through
it by the carriage clamped to it, so a belt is a shape to be re-drawn
at every position rather than a part to be re-placed, and the design's
2 mm ring hulled around a few circles has nowhere to put a tooth.  Both
belts are now what they are on the machine: GT2, toothed, clamped to
the thing they pull, drawn afresh from wherever that thing is.  Both
motors that drive one have the pulley the design's own bill of
materials buys and its module never drew, and the X one is meshed:
what a GT2 belt and its pulley are lives in `gt2.py`, the part is in
`hardware/gt2_pulley.py`, and the loops themselves are in
`x_stage/x_belt.py` and `y_axis/y_belt.py`.

The springs are the other thing that is not where it is put, and they
are the plainer case.  A belt's shape follows the machine because the
rubber inside a standing loop travels; a spring's shape follows the
machine because the thing is shorter when you press on it.  The design
buys six and draws none, in two blocks it heads "TODO: Add these parts
to the CAD model": four hold the heated bed up off the Y platform so a
nut at each corner can pull it down until the bed is level, and two
ride the extruder handle's long bolts and press the idler onto the
filament.  What a compression spring is here is in `spring.py`; the
parts are in `y_axis/platform/` and `x_stage/carriage/extruder/`.

Two things about them are worth knowing without reading further.  The
bill of materials names a spring the way a catalogue does -- a
reference, an outside diameter, a free length -- and says nothing about
the wire or the number of turns, which are the two numbers a drawing
needs; so both are derived from what has to fit, and both come out
round for both springs.  And a spring is drawn to the room its
neighbours leave rather than to a length written down, which is how the
bed's turned out to be a place the design states one distance twice and
disagrees with itself by three tenths of a millimetre.

And then there is the hot end, which is neither a shape that follows
the machine nor a part the design forgot to buy.  It is the thing the
machine is measured from: `nozzle_tip_distance` lifts the whole X
platform so that the nozzle tip stands `ZCarPosition` above the build
surface and `HomeZ` brings it down onto the glass, and until now no
drawn part reached that point, because the one file that would draw the
PEEK body -- `jhead.scad` -- still carries the conflict markers of a
merge that was never finished, so OpenSCAD drops the module and the
whole machine has been rendering with nothing under the carriage.

So the five parts the bill of materials buys are here: the PEEK holder,
the PTFE liner down it, the brass nozzle screwed into its foot, and the
heater resistor and thermistor in the two holes the nozzle's block is
drilled with.  The nozzle is the design's own module; the other four are
drawn from the two dimensioned shop drawings this repository has always
carried in `doc/`.  What a J-head is here is in `jhead.py` and the parts
are in `x_stage/carriage/extruder/hotend/`.

Two of its numbers are derived rather than read off a drawing, and both
because the drawings leave them open where the machine does not.  The
holder's length, because its drawing says "36.5mm or 50mm (length not
critical)" and the machine says the tip has to land exactly
`jhead_length` less `jhead_instalation_depth` below the extruder.  And
the bore, because no drawing states it: it is the groove root the
design's own sketch draws its body around, less the thinnest wall that
sketch's drawing leaves at a groove, and what makes that worth anything
is that the liner the design draws goes down it with half a tenth of a
millimetre to spare.  The liner's own length then follows, and it is the
second place -- after the bed springs -- where the design states a
length for a gap and its own parts leave a different one.

The last thing to arrive is the one the machine eats.  The design says
what the filament is three times -- `diameter=3` declared on its own
line in the file that draws the reel and used by nothing in it, a PTFE
liner bored 3.0 for it, a 3.2 channel cut up the middle slice of the
extruder for it to arrive by -- and draws it nowhere, so the stand
beside the machine held a plain tube of ABS with nothing between it and
the extruder.

Now it holds a reel with its outermost layer drawn as the strand it is,
and that strand runs on to the machine.  It is the third flexible leaf
here and the one the other two are not: a belt's loop stands still
while the rubber inside it travels, a spring is shorter when you press
on it, and this is a length of stock hanging between a stand that never
moves and a print head that moves in X and in Z.  Drive either and the
run is drawn again from wherever the head has got to, while the turns
on the reel stay exactly where they are, because a reel does not turn
when a carriage does.  What filament is here is in `filament.py`.

The layer is not chosen either.  A wound turn lies against the last
one, so its pitch is the stock's own diameter and its count is however
many whole turns of that the reel's width holds -- fifty-three, of the
reel's hundred and sixty.  The tube under them is drawn to what is
wound below the layer, so the reel still comes to the diameter the
design draws it at, and its outside is now made of turns.

Getting there is not a straight line either.  The stand is beside the
machine and the extruder is inside it, so a run drawn from one to the
other goes through the frame's right-hand side panel, the beam's own
plate and the box at the beam's end.  It is carried over the machine's
own edge instead, comes across at that height until it is over the
extruder, and turns down into the channel through the opening the top
panel is cut with for the carriage to travel in -- which is why the
free run is pinned at three points rather than one, and why five ports
and not three: two of the three points share the plane the run comes in
on, and the third is made of the other two.

How high it crosses is the machine's own answer to a question the frame
cannot answer.  The frame's ceiling is the rod-end plates on its top
panel, and for a while the run crossed two stock diameters over those,
on the reasoning that nothing on this machine stands higher.  That is
not so: `ZCarPosition` is the middle of the Z travel, not the top, and
at the top the beam carries the extruder out through the top panel's
own opening with the handle plate thirty millimetres above the channel
mouth.  So the run is pinned over the highest the print head ever
stands, and by enough that the turn down onto it has room at every
corner of the two travels -- both of which are asked for rather than
described.

Where the run stops is a finding rather than a choice, and there are
four of them.  The first is at the mouth itself: the extruder handle's
plate stands on the block's top face three tenths of a millimetre
inside the channel it is beside, so the machine's own parts leave 2.9
mm of clear channel for 3 mm of stock and the strand grazes the plate
going in.  Below it the hobbed bolt and the idler bearing are drawn
into each other where the stock would be gripped, because the design
draws the idler shut and gives no knob for opening it.  Below them the
hot end is drawn on the filament axis at nought while the extruder cuts
its channel, its two M3 holes and its nozzle-holder slot three tenths
of a millimetre to one side, so the two disagree about where the
filament goes -- the second place, after the bed springs, where the
design states one thing twice.  And below that the liner's bore is 3.0
and so is the stock, which is a bore the size of what runs down it
rather than a fit anything can be drawn in.  All four are asked for by
contract, so none of them can quietly go away.

Where the geometry comes from is in `scad.py`, where the dimensions
come from is in `params.py`, and how a part is authored is in
`part.py`.
"""

from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, Instruction

from metamaquina2 import filament, z_screw
from metamaquina2.electronics.electronics import Electronics
from metamaquina2.filament import Filament
from metamaquina2.frame.frame import Frame
from metamaquina2.params import (
    BuildPlatform_height,
    BuildVolume_X,
    BuildVolume_Y,
    BuildVolume_Z,
    XCarPosition,
    XZStage_offset,
    YCarPosition,
    ZCarPosition,
    filament_diameter,
    machine_x_dim,
    nozzle_tip_distance,
)
from metamaquina2.spool_holder.spool_holder import SPOOL_HEIGHT, SpoolHolder
from metamaquina2.x_stage.x_stage import (
    TOP as TOP_OF_THE_BEAM,
    XStage,
    filament_entry,
)
from metamaquina2.y_axis.y_axis import YAxis
from metamaquina2.z_axis.z_axis import ZAxis


#: Where the free run gets over this machine, along the machine's own x.
#:
#: The stand is beside the machine and the extruder is inside it, so
#: the run has to get over the frame's right-hand side panel, which is
#: a wall of sheet from the floor to the frame's own height.  It
#: crosses at the machine's own edge, which is the last place before
#: the frame there is nothing but air.
CROSSING_X = machine_x_dim / 2

#: How high the run crosses, and comes across at until it is over the
#: extruder.
#:
#: Over the highest this machine ever stands, which is not the frame.
#: The rod-end plates on the top panel are the frame's own ceiling at
#: 369, but `ZCarPosition` is the middle of the Z travel and not the
#: top of it: wind the beam up to `BuildVolume_Z` and it carries the
#: extruder's channel mouth to 366 and the handle plate 30 mm above
#: that, out through the opening the top panel is cut with.  So what
#: the run has to get over is the print head, and the height it gets
#: over it by is measured from the beam rather than from the frame.
#:
#: The clearance is chosen and not derived, and it is not small.  Two
#: stock diameters -- enough for a run passing over a fixed sheet -- is
#: not enough for one turning down onto a moving head: with the beam at
#: the top of its travel and the carriage at the far end of the beam,
#: the turn swings wide and reaches the handle bolts standing out in
#: front of the block.  Twelve leaves the turn its room at every corner
#: of the two travels, and what makes that a claim rather than a guess
#: is `test_the_free_run_gets_over_the_machine_rather_than_through_it`,
#: which asks the metal at all four of them.
CROSSING_CLEARANCE = 12 * filament_diameter
CROSSING_Z = (BuildPlatform_height + BuildVolume_Z + nozzle_tip_distance
              + TOP_OF_THE_BEAM + CROSSING_CLEARANCE)


class Metamaquina2(AssemblyNode):
    """The complete Metamaquina 2 desktop 3D printer.

    The three drivers are declared here, on the machine, rather than
    one per axis, because that is where a maker meets them: the
    coordinates on the panel of a printer are the printer's, not the
    X carriage's opinion of its own beam.  Every one of them is read
    and set in millimetres in the design's own coordinates, which is
    what makes `XCarPosition` a default and not a conversion, and the
    travel each declares is the build volume the machine advertises:
    X and Y reach half of it either side of centre, and Z counts the
    nozzle up from the bed to the full height.

    Underneath, Z is the odd one and is meant to be.  X and Y are
    pulled by belts, and a belt has no state a millimetre does not
    already say; Z is turned by screws, and a screw's state is an
    angle.  So `z` holds degrees and declares the `scale` that makes
    them millimetres, which is exactly the machine: a hundred and
    twenty turns of a right-handed M8 bar, and the beam is at the top
    of its travel.  A maker never sees that -- the slider, the readout
    and every instruction target below are in millimetres -- but the
    bars do, and it is why they can be drawn turning.

    The instructions are what a maker can press, and `HomeZ` is the one
    that shows what the change is for.  Home on this axis is the bottom,
    where the nozzle meets the build surface and the endstop is, and
    getting there takes the time a screw takes: `z_screw.HOMING_TIME`
    is the whole declared travel at Marlin's own Z homing feedrate, and
    that is nearly forty seconds of watching the bars turn.  That is
    not a slow animation, it is the machine.
    """

    # where the stand sits beside the machine
    spool_holder_position = [400, 0, 0]

    x = Driver(default=XCarPosition, unit='mm',
               range=(-BuildVolume_X / 2, BuildVolume_X / 2))
    y = Driver(default=YCarPosition, unit='mm',
               range=(-BuildVolume_Y / 2, BuildVolume_Y / 2))
    z = Driver(default=z_screw.angle(ZCarPosition), unit='mm',
               range=(0, BuildVolume_Z), scale=z_screw.SCALE)

    instructions = {
        # Back to the pose the design draws, all three axes at once.
        # It is not called Home because it is not: two of these are the
        # middle of their travel and the third is the top of it.
        'Rest': Instruction({'x': XCarPosition,
                             'y': YCarPosition,
                             'z': ZCarPosition},
                            duration=z_screw.HOMING_TIME),
        # The carriage crosses to the middle of the bed.
        'CenterX': Instruction({'x': 0.0}, duration=2.0),
        # The bed comes forward, out from under the arc panel at the
        # back, which is how a finished print is reached.
        'PresentBed': Instruction({'y': -BuildVolume_Y / 2}, duration=2.0),
        # Z goes home, and home is the bottom: the screws wind the beam
        # down until the nozzle is on the build surface.
        'HomeZ': Instruction({'z': 0.0}, duration=z_screw.HOMING_TIME),
    }

    def __init__(self, *args, **kwargs):
        self.frame = Frame()

        self.z_axis = ZAxis()
        self.y_axis = YAxis()
        self.x_stage = XStage()

        self.electronics = Electronics()

        self.spool_holder = (SpoolHolder()
                             .rotate(90, [0, 0, 1])
                             .translate(self.spool_holder_position))

        # Where the reel's axis stands, in the machine's coordinates.
        # The stand is turned a quarter turn to put its bar across the
        # machine, and a point on the stand's own axis does not move
        # when it is turned about that axis, so the reel's centre is
        # simply the stand's position and the height it hangs the reel
        # at.
        reel = [self.spool_holder_position[0],
                self.spool_holder_position[1],
                self.spool_holder_position[2] + SPOOL_HEIGHT]

        #: Where the strand's own frame stands.  Held on the machine
        #: rather than worked out twice, because `render` has to read a
        #: point of the machine back in that frame every time it binds
        #: the run's far end.
        self.strand_origin = [reel[axis] + filament.OFFSET[axis]
                              for axis in range(3)]

        self.filament = (Filament()
                         .rotate(*filament.PLACEMENT)
                         .translate(self.strand_origin))

        super().__init__(*args, **kwargs)

    def render(self):
        """Place what the drivers move, then hand over the children.

        X and Y are relayed into the axis that owns the moving frame,
        because the carriage and the bed are placed inside their own
        assemblies.

        Z is told twice, because a screw drive is two statements about
        one number.  The axis is told how far its bars are turned, plus
        the constant `z_screw.PHASE` that lines their thread up with the
        nuts the beam hangs on -- the turn a builder puts in once, with
        the screws in their hands, and never again.  Then the stage is
        lifted to what that turn is worth.  The lift is a translate here
        rather than a port because the machine itself is what holds the
        beam at a height; what the beam hangs FROM is in the Z axis, and
        the two agree because both are read off the same screw.

        The filament is told the points its free run is pinned at, and
        one of them is the same lift a third time.  The beam says where
        its extruder's channel opens in its own frame, the machine adds
        what it stood the beam off by, and `in_strand_frame` reads the
        result back in the strand's own turned frame.  The other is
        where the run gets over the machine, which is the machine's to
        say because both the frame it has to clear and the height its
        own head reaches are: a point of air off the machine's own edge,
        above the top of the beam at the top of its travel, in the plane
        the run comes in on.

        Five ports rather than two, because a point is three numbers and
        a molejo parameter is a plain named number with no arithmetic
        behind it -- and five rather than six because the two points
        share that plane.  The third pinned point, where the run turns
        down, is bound to no port of its own: it is the crossing's own
        height with the end's own two numbers, so the shape makes it out
        of ports already bound.
        """
        self.connect(self.x, self.x_stage.carriage_position)
        self.connect(self.y, self.y_axis.platform_position)
        self.connect(self.z + z_screw.PHASE, self.z_axis.screw)

        stage = [0, -XZStage_offset,
                 BuildPlatform_height + z_screw.lift(self.z)
                 + nozzle_tip_distance]
        self.x_stage.translate(stage)

        entry = filament_entry(self.x)
        entry = [entry[axis] + stage[axis] for axis in range(3)]
        head = filament.in_strand_frame(entry, self.strand_origin)
        over = filament.in_strand_frame(
            [CROSSING_X, entry[1], CROSSING_Z], self.strand_origin)

        self.connect(over[0], self.filament.over_x)
        self.connect(over[1], self.filament.over_y)
        self.connect(head[0], self.filament.head_x)
        self.connect(head[1], self.filament.head_y)
        self.connect(head[2], self.filament.plane)

        return [self.frame, self.z_axis, self.y_axis, self.x_stage,
                self.electronics, self.spool_holder, self.filament]
