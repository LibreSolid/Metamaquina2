"""The GT2 pulley on a motor shaft."""

import math

from solid2 import polygon

from metamaquina2 import gt2, materials
from metamaquina2.params import motor_shaft_diameter
from metamaquina2.part import ScadPart, curve


#: How many teeth the pulley of this machine has.
#:
#: Sixteen, because that is the pulley the machine buys: "GT2 pulley
#: 6mm x 16 teeth", ref GT2P6x16_Al, called out once at each belt
#: motor.  Nothing in the design was derived from that line -- it is a
#: string handed to the bill of materials from inside a module that
#: draws nothing -- and the number the design did derive from,
#: `PulleyRadius`, said 6, which is no pulley at all.  The bought part
#: is the one that ends up on the shaft, so the design was corrected to
#: it rather than the other way about, and `PulleyRadius` is now 4.839:
#: where sixteen GT2 teeth carry a belt.
TEETH = 16

#: How wide it is, in millimetres of belt.
#:
#: The other half of the same BOM line.  A 6 mm pulley is what is
#: bought, and the design draws a 5 mm belt while buying 6 mm belt too,
#: so the part is drawn at its own width and stands half a millimetre
#: proud of the belt on each side.  Which of those two widths the
#: design meant is not this part's to decide; see `gt2`.
WIDTH = 6


class GT2Pulley(ScadPart):
    """The toothed pulley a GT2 belt is driven from.

    Drawn here rather than called out of the design like every other
    bought part, because the design's `GT2_pulley` is an empty stub:
    a bill-of-materials line and a `//TODO: implement-me!`.  Its form
    could not be recovered from the .scad even in principle -- what
    makes a pulley mesh is that its surface is the belt's inner
    surface, and the belt's inner surface is molejo's, so the two are
    authored from the one description of a GT2 tooth in `gt2`.

    What `outline` returns is not a cylinder with notches cut in it and
    not the tooth's own shape either: it is `gt2.groove`, the deepest a
    tooth reaches anywhere on its way in and out.  A trapezoid cannot
    leave a trapezoid, so the flanks are scooped back where a tooth
    swings through them, while the floor and the land between two
    grooves -- the two surfaces that carry -- keep the shape the tooth
    gives them and only stand off it by `CLEARANCE`.  So a belt drawn
    around this circle and a pulley drawn at this phase are nested
    without touching, at every position of the axis rather than at the
    seated one alone.

    The pulley is drawn with a groove centred on its own +X, which is
    the phase reference whatever places it turns: an assembly puts a
    groove where the belt puts a tooth by rotating this part, never by
    redrawing it.  It is rigid, like every bought part -- it turns, it
    does not change shape.

    No flanges.  A real GT2 pulley has them and the design gives no
    dimension for them, so the part is drawn as the toothed body alone,
    at the width the bill of materials buys it at.
    """

    color = materials.METAL

    #: How much smaller than the belt's inner surface the pulley is cut.
    #:
    #: A pulley drawn exactly on that surface is not wrong so much as
    #: over-precise: it claims the two parts share every square
    #: millimetre of skin they meet on, which no pulley is machined to
    #: and no belt is moulded to, and which a real belt takes up by
    #: flexing onto
    #: whatever it finds -- that is what the rubber is for.  It is also
    #: a claim no mesh can hold: coincident surfaces come out of a
    #: boolean as slivers with a volume, so a drawing that puts them
    #: there cannot afterwards be asked whether the two parts
    #: interfere.
    #:
    #: A tenth of a millimetre, taken off everywhere.  Small against
    #: the 0.17 mm the flanks are already scooped back by, which is a
    #: shape and not a tolerance; large against anything the outline
    #: resolves; and about what a machined pulley and a moulded belt
    #: really run with.
    #:
    #: The bore gets it too, opened rather than cut back, and for the
    #: second half of the same reason.  A bore drawn at exactly the
    #: shaft's nominal radius is not a slip fit, it is the same circle
    #: twice -- and two OpenSCAD circles of one radius are two polygons
    #: whose flats fall inside it, so at any relative angle but the one
    #: where their vertices coincide each pokes through the other.  Five
    #: hundredths of a cubic millimetre of it, which showed the moment
    #: this pulley began to turn.  A real pulley is bored a little over
    #: its shaft and pinched onto it with a grub screw.
    #:
    #: It is also the measured figure.  Where a tooth is halfway out of
    #: a groove the drawn belt still grazes the drawn pulley by a few
    #: hundredths, and how much depends on where in a tooth the
    #: carriage happens to stand -- so the worst of it was looked for
    #: over a whole tooth of travel rather than at the rest pose.  Half
    #: this leaves 0.022 cubic mm at the worst phase; this leaves
    #: 0.00004, which is the dust of a mesh boolean rather than a bite.
    CLEARANCE = 0.1

    #: Points spent on each quarter of a tooth.
    #:
    #: A tooth is four quarters -- groove floor, flank, land, flank --
    #: so this is also where the corners between them fall: a multiple
    #: of four puts a point on each of them, which is what keeps a chord
    #: from cutting a corner off the floor or the land.  Sixteen brings
    #: sixteen teeth to 1024 points, about sixteen times finer than the
    #: design's own `$fs` would draw a circle this size, and it is what
    #: sets the flank clearance: `gt2.groove` sinks every point to the
    #: deepest of its own step, so a coarser outline would be a slacker
    #: pulley.  At this count the flanks are cut back 0.17 mm because a
    #: tooth needs it and a further 0.08 because the polygon is a
    #: polygon, which together is about the backlash a real GT2 pulley
    #: is made with.
    SAMPLES = 16

    def __init__(self, period=gt2.PITCH, teeth=TEETH, width=WIDTH,
                 bore=motor_shaft_diameter, **kwargs):
        self.period = period
        self.teeth = teeth
        self.width = width
        self.bore = bore
        super().__init__(period, teeth, width, bore, **kwargs)

    @property
    def radius(self):
        """The flank circle this pulley is drawn from: where a belt's
        land between two teeth rides, and so the circle every depth in
        `outline` is measured inward from.  The metal itself stops
        `CLEARANCE` short of it."""
        return gt2.pulley_radius(self.teeth, self.period)

    def outline(self):
        """The section the pulley is cut from.

        One groove, worked out once by `gt2.groove`, then stamped round
        the circle `teeth` times -- because a pulley has one groove
        shape and every tooth of the belt goes through every one of
        them.  Walked counter-clockwise from a groove centre at angle
        nought, at `SAMPLES` points per quarter tooth, and everywhere
        `CLEARANCE` inside where the belt would put it.
        """
        depths = gt2.groove(self.teeth, self.period, 4 * self.SAMPLES)
        points = []
        for tooth in range(self.teeth):
            for step, depth in enumerate(depths):
                angle = (2 * math.pi
                         * (tooth + step / len(depths)) / self.teeth)
                radius = self.radius - depth - self.CLEARANCE
                points.append([radius * math.cos(angle),
                               radius * math.sin(angle)])
        return points

    def render(self):
        section = polygon(self.outline()) - curve(
            'circle', r=self.bore / 2 + self.CLEARANCE)
        return section.linear_extrude(self.width)
