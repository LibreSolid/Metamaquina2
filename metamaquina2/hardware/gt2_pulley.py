"""The GT2 pulley on a motor shaft."""

import math

from solid2 import polygon

from metamaquina2 import gt2, materials
from metamaquina2.params import PulleyRadius, belt_width, motor_shaft_diameter
from metamaquina2.part import ScadPart, curve


#: How many teeth the pulley of this machine has.
#:
#: The design never says.  It writes `PulleyRadius = 6` and buys "GT2
#: pulley 6mm x 16 teeth" in the bill of materials, and those are two
#: different pulleys: 16 teeth put the flanks at 4.836, more than a
#: millimetre inside the radius the design draws its belt around, while
#: 6 is 0.112 short of the 20 tooth pulley it very nearly is.  The
#: geometry is what the rest of the machine is built on -- `XIdler_height`
#: and `X_rod_height` are both derived from `PulleyRadius` -- and the
#: BOM line is a string nothing is derived from, which also calls the
#: belt 6 mm wide where `belt_width` is 5.  So the geometry is taken as
#: the design's real intent and the tooth count follows from it.
TEETH = gt2.pulley_teeth(PulleyRadius)


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
    exactly as wide as the belt it carries.
    """

    color = materials.METAL

    #: How much smaller than the belt's inner surface the pulley is cut.
    #:
    #: A pulley drawn exactly on that surface is not wrong so much as
    #: over-precise: it claims the two parts share sixteen square
    #: millimetres of skin, which no pulley is machined to and no belt
    #: is moulded to, and which a real belt takes up by flexing onto
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
    #: twenty teeth to 1280 points, about sixteen times finer than the
    #: design's own `$fs` would draw a circle this size, and it is what
    #: sets the flank clearance: `gt2.groove` sinks every point to the
    #: deepest of its own step, so a coarser outline would be a slacker
    #: pulley.  At this count the flanks are cut back 0.17 mm because a
    #: tooth needs it and a further 0.08 because the polygon is a
    #: polygon, which together is about the backlash a real GT2 pulley
    #: is made with.
    SAMPLES = 16

    def __init__(self, period=gt2.PITCH, teeth=TEETH, width=belt_width,
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
        section = polygon(self.outline()) - curve('circle', r=self.bore / 2)
        return section.linear_extrude(self.width)
