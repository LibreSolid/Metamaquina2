"""What the hot end of this machine is, and where its parts stand.

The J-head is five bought parts: a nozzle holder turned from 5/8" round
PEEK, a PTFE liner down the middle of it, a brass nozzle screwed into
its foot, and in the nozzle's block a heater resistor and a thermistor.
The bill of materials buys all five -- `MM2_PEEK`, `MM2_PTFE_liner`,
`035_NZ`, `UB5C-5RF1`, `TV100000X` -- and three of them under blocks
headed ``//TODO: Add this part to the CAD model``.

Where the numbers come from
---------------------------

Two dimensioned shop drawings, both in ``doc/`` and both cited on the
constants they give:

* ``Jhn_nozzle_holder_v4.jpg`` -- "Nozzle Holder Version 4", the PEEK
  part, in inches with a millimetre mount end.
* ``Jhn_md_brass_heater_nozzle.jpg`` -- "J-Head Plastic Extrusion
  Nozzle", the brass part, in inches.  ``nozzle.scad`` is that drawing
  already transcribed into OpenSCAD, so the nozzle is called and not
  redrawn; what is restated here is only the handful of its numbers
  something outside it has to stand on.

Why `jhead.scad` is not used
----------------------------

The design does have a module for the PEEK body, and OpenSCAD has never
seen it.  ``jhead.scad`` still carries the conflict markers of a merge
that was never finished -- at line 107, over two cut cubes that remove
nothing from the body in either version, one cutting at +-18 mm and the
other at +-11.5 mm of a body whose own radius is 8 -- so the parser
gives up on the file and every caller gets ``WARNING: Ignoring unknown
module 'J_head_assembly'``.  The whole-machine rendering has been coming
out with nothing under the carriage ever since.

Repairing it is not this layer's to do, and would not help much if it
were.  What the file sketches is a stack of discs: a plain core running
the whole length with fins around its middle, no collar, no neck, no
tapped bores, and a tip 1.8 mm short of the `jhead_length` the machine
measures Z from.  So the holder is drawn here, from its own drawing, and
the one number the sketch is worth keeping -- the +-10.4 core its fins
stand out from, which is the diameter the grooves are milled down to --
is restated in `params` with the module it belongs to.

The two numbers that are derived
--------------------------------

Everything else is off a drawing.  These two are not, and both for the
same reason: the drawings leave them open and the machine does not.

`body_length`, because the holder's drawing says "36.5mm or 50mm
(length not critical)" and the machine's own `nozzle_tip_distance`
lifts the entire X platform by `jhead_length` less
`jhead_instalation_depth`, so that the nozzle tip stands exactly
`ZCarPosition` above the build surface and `HomeZ` brings it down onto
the glass.  A holder drawn at either of the drawing's two lengths puts
the tip somewhere else and makes the machine's own Z zero a fiction.
So the length is what leaves the tip where the machine says it is, and
it comes out at 42.277 mm of 5/8" body, 52.947 mm of holder.

`bore`, because no drawing states it.  The holder's grooves are milled
down to the +-10.4 the design's own sketch draws its body around, and
the drawing leaves a wall of 0.078" to 0.094" between a groove's floor
and the bore.  Only the thin end of that range leaves a bore the
design's own PTFE liner passes down: +-6.4376 over a +-6.33 liner, 0.054
mm of clearance all round, which is the press fit a PTFE liner is
really fitted with.  The fat end would give +-5.62 and no liner at all.

And one length that follows from them: the liner's.  Between the
holder's top face and the rim its point comes to rest on there are
40.3 mm, and ``PTFE_liner.scad`` draws a 47 mm liner.  They cannot both
be right -- the stub tops out where it tops out however far the nozzle
is screwed in, because the block bottoms on the holder's own shoulder --
so the liner is drawn to the room its neighbours leave it, as the bed
springs are, and `LINER_SHORTFALL` is the disagreement.
"""

import math

from metamaquina2.params import (
    PTFE_liner_diameter,
    PTFE_liner_length,
    PTFE_liner_point,
    PTFE_liner_tip,
    inch,
    jhead_groove_root,
    jhead_instalation_depth,
    jhead_length,
)


########################################
# The nozzle holder, from Jhn_nozzle_holder_v4.jpg.
#
# Its mount end is drawn in millimetres and everything below the mount
# plane in inches, which is how the drawing has it: the collar and neck
# are what an extruder built in millimetres has to clamp, and the body
# is a length of American bar stock.

#: The collar at the very top, and the neck under it that the extruder's
#: slot closes around.  Their two lengths add up to 9.4, which is the
#: design's own `jhead_instalation_depth` -- the two numbers meet, and
#: `INSTALLATION` below is where that is checked rather than assumed.
COLLAR_DIAMETER = 12.0
COLLAR = 4.76
NECK_DIAMETER = 6.5
NECK = 4.64

#: The bar it is turned from: 5/8" round PEEK.
BODY_DIAMETER = inch * 5 / 8

#: The shoulder at the foot, which the drawing calls optional and gives
#: as 0.500 -0.000 +0.003 by 0.050 long.  It is the same 0.500" across
#: as the nozzle's heater block is square, so it lands centred on the
#: block's top face and stands the PEEK off the brass.
SHOULDER_DIAMETER = inch * 0.500
SHOULDER = inch * 0.050

#: The cooling grooves.  The drawing gives one and a rule for the rest:
#: "Typical Groove: 2mm to 0.094 (not critical). Centers of each groove
#: are 0.125 apart", and locates the one it draws 0.450" up from the
#: foot.  How many there are it does not say; `jhead.scad` sketches
#: five, which is the design's own answer and the one taken here.
GROOVES = 5
GROOVE = 2.0
GROOVE_PITCH = inch * 0.125
FIRST_GROOVE = inch * 0.450

#: What is left standing between a groove's floor and the bore, at the
#: thin end of the drawing's "0.078-0.094".  See the module docstring
#: for why it is the thin end.
GROOVE_WALL = inch * 0.078

#: Where the grooves are cut and where they are not: "Grooves are milled
#: between the following angles: 0-90, 120-210, 240-330", which leaves
#: three thirty-degree supports carrying the foot.
GROOVE_SECTORS = ((0, 90), (120, 210), (240, 330))

#: The two tapped bores, drawn at their tap drills, which is the
#: material a tap leaves.  5/16-24 at the top, 0.200" deep, letter I;
#: 3/8-24 at the foot, threaded 0.460" deep, letter Q.  The foot's hole
#: is drilled further than it is threaded -- up until it meets the
#: filament bore, as it must be for the filament to reach the nozzle --
#: so only its diameter is used here and its depth comes out of the
#: stack.
TOP_TAP_DRILL = inch * 0.272
TOP_TAP_DEPTH = inch * 0.200
NOZZLE_TAP_DRILL = inch * 0.332
NOZZLE_TAP_DEPTH = inch * 0.460


########################################
# The brass nozzle, from Jhn_md_brass_heater_nozzle.jpg by way of
# v4nozzle() in nozzle.scad, which is that drawing transcribed.  Only
# the numbers something outside the module has to stand on are here.

#: The heater block: 0.500" square in plan, 0.325" tall, with the
#: filament axis 0.15625" from one face and 0.250" from the next.  The
#: offset is why the block is not centred on the hot end's axis: it
#: leaves the room the heater resistor is drilled into.
BLOCK = inch * 0.500
BLOCK_HEIGHT = inch * 0.325
BLOCK_BORE_X = inch * 0.15625
BLOCK_BORE_Y = inch * 0.250

#: The threaded stub above the block: 0.350" of 3/8-24 and 0.150" turned
#: down over it, which is the drawing's "turn off top 3 threads".
STUB = inch * (0.350 + 0.150)

#: How far below the block the brass reaches: a 0.050" projection and
#: then 0.070" of nozzle cone down to the orifice.
REACH = inch * (0.050 + 0.070)

#: The melt chamber bored up the middle of the stub, which opens at the
#: stub's top face.  This is what the liner comes down onto: not the
#: face, but the rim of this hole.
MELT_CHAMBER = inch * 2 * 0.069

#: The two holes the module drills into the block, as the diameter and
#: the depth of each, and where each one starts, measured from the
#: filament axis and from the block's base.  The heater hole goes right
#: through along Y; the thermistor hole enters the -X face and stops.
HEATER_DIAMETER = inch * 2 * 0.117
HEATER_HEIGHT = inch * 0.1625
HEATER_X = inch * (0.358 - 0.15625)
THERMISTOR_DIAMETER = inch * 2 * 0.045
THERMISTOR_DEPTH = inch * 0.170
THERMISTOR_HEIGHT = inch * 0.1625
THERMISTOR_Y = inch * (0.430 - 0.250)
THERMISTOR_FACE = inch * (0.001 + 0.15625)


########################################
# How much under a hole a part pressed into it is drawn.

#: A tenth of a millimetre, for the same reason the GT2 pulley is bored
#: a tenth over its shaft.  A resistor drawn at exactly the diameter of
#: the hole it is drilled into is not a fit, it is the same circle
#: twice -- and two OpenSCAD circles of one radius are two polygons
#: whose flats fall inside it, so at any relative angle but one each
#: pokes through the other, and the pair can no longer be asked whether
#: they interfere.  Small against anything either outline resolves,
#: large against nothing.
FIT = 0.1


########################################
# The stack, from the mount plane down.
#
# Zero is the face the extruder's underside clamps the holder against,
# which is the top of its 5/8" body, and +Z is up.  Every part of the
# hot end is placed from one of these.

#: How much of the holder stands inside the extruder block: the collar
#: and the neck, and so also the design's own `jhead_instalation_depth`.
#: Written as the sum rather than as the probed value so that the
#: drawing and the design have to agree, and a contract asks them to.
INSTALLATION = COLLAR + NECK

#: How far below the mount plane the nozzle tip stands.  Not a choice:
#: it is what `nozzle_tip_distance` lifts the whole X platform by.
TIP = jhead_length - jhead_instalation_depth

#: The 5/8" body's length -- the free number, carrying the whole stack.
#: What is left of `TIP` once the holder's own shoulder and the brass
#: below the block have taken their share.
body_length = TIP - SHOULDER - (BLOCK_HEIGHT + REACH)

#: The face the shoulder presents to the nozzle, and so also where the
#: heater block's top face stands: the nozzle is run in until the two
#: meet.
FOOT = -(body_length + SHOULDER)

#: Where the nozzle's threaded stub tops out inside the holder, which is
#: what the liner comes down onto.
STUB_TOP = FOOT + STUB

#: The filament bore: the groove root, less the wall the drawing leaves
#: on each side of it.
bore = jhead_groove_root - 2 * GROOVE_WALL

#: How long the drill point on the end of the liner is, from the
#: design's own outline: a 118 degree cone from the tube's diameter down
#: to its tip.
LINER_POINT = ((PTFE_liner_diameter - PTFE_liner_tip) / 2
               / math.tan(math.radians(PTFE_liner_point / 2)))

#: How high above the stub's top face the liner's shoulder comes to rest.
#:
#: The point on the end of the liner is a drill's point, cut to sit in
#: the conical bottom a drill leaves.  There is no such cone here: what
#: is under it is the flat top of the nozzle's stub with the melt
#: chamber opening through it, so the cone lands on that rim, at
#: whatever depth along itself it has narrowed to the chamber's own
#: diameter.  Only the last 0.08 mm of the tip goes in.
LINER_SEAT = ((PTFE_liner_diameter - MELT_CHAMBER) / 2
              / math.tan(math.radians(PTFE_liner_point / 2)))

#: How much room the liner has to run in: from the holder's top face
#: down to where its point comes to rest on the chamber's rim.  This is
#: the liner's own cylindrical length; the point stands below it.
liner_length = INSTALLATION - STUB_TOP - LINER_SEAT

#: What the design's own liner drawing asks for, less what the hot end
#: leaves it.  ``PTFE_liner.scad`` draws 47 mm of liner and there are
#: 40.3 mm between the holder's top face and the rim the point sits on,
#: so 6.7 mm of it has nowhere to be: above the holder is the extruder's
#: own +-3.2 filament channel, which a +-6.33 tube does not enter, and
#: below the rim is the +-3.5 melt chamber, which it does not enter
#: either.  The placements win and this is the size of the disagreement,
#: published so a contract can ask for it rather than letting it quietly
#: go away.
LINER_SHORTFALL = PTFE_liner_length - (liner_length + LINER_POINT)
