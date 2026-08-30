"""The PEEK nozzle holder: the cold half of the hot end."""

import math

from solid2 import polygon

from metamaquina2 import jhead, materials
from metamaquina2.params import epsilon, jhead_groove_root
from metamaquina2.part import ScadPart, curve


#: How many points a milled sector's outer edge is walked with.
#:
#: The edge is a chord run outside the bar and cut away with it, so it
#: never reaches the part; what it has to do is stay outside a 5/8" body
#: over ninety degrees, which eight steps of eleven degrees does with
#: nine tenths of a millimetre to spare.  The two edges that do reach
#: the part -- the radial flanks of the cut and the groove's own floor
#: -- are a straight line and a `curve` circle, and neither is sampled
#: here.
SECTOR_SAMPLES = 8

#: How far outside the bar a sector's outer edge is drawn.
SECTOR_MARGIN = 1


class NozzleHolder(ScadPart):
    """The 5/8" PEEK bar the hot end hangs from, on the mount plane.

    Drawn from `doc/Jhn_nozzle_holder_v4.jpg`, which is the dimensioned
    shop drawing of this exact part, because the design's own module for
    it is in a file OpenSCAD cannot parse -- `jhead` says what happened
    to `jhead.scad` and why it is not repaired here.

    Its origin is the mount plane: the shoulder where the 5/8" body
    stops and the collar and neck go up into the extruder block.  So the
    collar and neck stand above z nought and everything else hangs below
    it, which is the one place in this part a builder can point at --
    the face that lands on the underside of the extruder.

    Two of its dimensions are not on the drawing.  The length of the
    body is derived, because the drawing calls it "not critical" and the
    machine calls it the thing Z is measured from; the bore is derived,
    because no drawing states it and the groove root and the wall
    around it do.  Both derivations are in `jhead`.

    What is on the drawing and is not drawn here: the note that the
    supports left between the milled sectors are themselves relieved by
    drilling at 15, 135 and 255 degrees.  That is a way of getting the
    cutter in rather than a feature of the part, and the cross section
    it points at shows the three supports the sectors leave, which is
    what is drawn.
    """

    color = materials.PEEK

    def sector(self, start, end):
        """A wedge of the bar between two angles, reaching past its
        skin."""
        radius = jhead.BODY_DIAMETER / 2 + SECTOR_MARGIN
        points = [[0, 0]]
        for step in range(SECTOR_SAMPLES + 1):
            angle = math.radians(
                start + (end - start) * step / SECTOR_SAMPLES)
            points.append([radius * math.cos(angle),
                           radius * math.sin(angle)])
        return polygon(points)

    def groove(self):
        """One groove's section: the milled sectors, down to the root.

        Three ninety-degree cuts at the drawing's own angles, everything
        outside the root circle taken away and everything inside it
        left, so what is left standing is the core plus the three thirty
        degree supports between the cuts.
        """
        cuts = self.sector(*jhead.GROOVE_SECTORS[0])
        for start, end in jhead.GROOVE_SECTORS[1:]:
            cuts += self.sector(start, end)
        return cuts - curve('circle', r=jhead_groove_root / 2)

    def grooves(self):
        """Every groove, up from the first one above the foot."""
        section = self.groove().linear_extrude(jhead.GROOVE)
        cut = None
        for number in range(jhead.GROOVES):
            height = (-jhead.body_length + jhead.FIRST_GROOVE
                      + number * jhead.GROOVE_PITCH)
            placed = section.translate([0, 0, height])
            cut = placed if cut is None else cut + placed
        return cut

    def bores(self):
        """The three holes drilled up the middle, foot to top.

        The 3/8-24 the nozzle screws into, drawn at its letter Q tap
        drill and drilled as deep as the stub it takes rather than as
        deep as the 0.460" it is threaded; the filament bore above it;
        and the 5/16-24 at the top, drawn at its letter I tap drill.
        Both ends are cut a hair proud of the faces they break through,
        the way the design's own `epsilon` is used everywhere else.
        """
        nozzle = curve(
            'cylinder', r=jhead.NOZZLE_TAP_DRILL / 2,
            h=jhead.STUB + epsilon,
        ).translate([0, 0, jhead.FOOT - epsilon])

        filament = curve(
            'cylinder', r=jhead.bore / 2,
            h=jhead.INSTALLATION - jhead.TOP_TAP_DEPTH - jhead.STUB_TOP,
        ).translate([0, 0, jhead.STUB_TOP])

        top = curve(
            'cylinder', r=jhead.TOP_TAP_DRILL / 2,
            h=jhead.TOP_TAP_DEPTH + epsilon,
        ).translate([0, 0, jhead.INSTALLATION - jhead.TOP_TAP_DEPTH])

        return nozzle + filament + top

    def bar(self):
        """The turned bar, before anything is cut out of it."""
        collar = curve(
            'cylinder', r=jhead.COLLAR_DIAMETER / 2, h=jhead.COLLAR,
        ).translate([0, 0, jhead.NECK])

        neck = curve('cylinder', r=jhead.NECK_DIAMETER / 2, h=jhead.NECK)

        body = curve(
            'cylinder', r=jhead.BODY_DIAMETER / 2, h=jhead.body_length,
        ).translate([0, 0, -jhead.body_length])

        shoulder = curve(
            'cylinder', r=jhead.SHOULDER_DIAMETER / 2, h=jhead.SHOULDER,
        ).translate([0, 0, jhead.FOOT])

        return collar + neck + body + shoulder

    def render(self):
        return self.bar() - self.grooves() - self.bores()
