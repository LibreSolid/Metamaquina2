"""The idler release handle, its bolts, and the springs on them."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bolt import Bolt
from metamaquina2.hardware.m4_washer import M4Washer
from metamaquina2.params import (
    HandleWidth,
    handle_bolt_length,
    handle_nut_height,
    m4_washer_thickness,
)
from metamaquina2.x_stage.carriage.extruder.handle_plate import HandlePlate
from metamaquina2.x_stage.carriage.extruder.idler.idler import Idler
from metamaquina2.x_stage.carriage.extruder.idler_spring import IdlerSpring


#: Where the extruder stands this assembly, and which way round.
#:
#: Named here rather than written into the extruder, because the handle
#: is the one part of the machine that has to know where something else
#: is: its bolts run through the idler's back plate, and the spring on
#: each of them stands on that plate's far face.  With the offset in
#: two places, a change to it would move the bolts and leave the
#: springs behind.
#:
#: The rotations that go with it turn the handle's own +z along the
#: extruder's -x, so a distance up a bolt from the handle plate is
#: `POSITION[0]` minus a position in the extruder's flat frame.
POSITION = [7, 0, 58]

#: How far up the handle plate the two bolts run, from `handle()`.
BOLT_ROW = 5

#: How far along a bolt the idler's back plate stands, measured the way
#: the bolt is drawn: from the handle plate's outer face towards the
#: head.  The spring on each bolt stands on that plate's far face,
#: which is the side compressing it swings the idler shut from.
SPRING_SEAT = POSITION[0] - Idler.back_face

#: How much bare shank the design leaves between the spring and the
#: bolt head.
#:
#: Not slack: it is the adjustment.  The run from the back plate to the
#: head is 25 mm and the washer and the spring are 17.25 of it, and
#: what takes up the rest is the lock nut the bill of materials buys
#: and no module draws.  Winding it in pulls the head down onto the
#: spring, which is how a maker sets how hard the idler grips.  The
#: design states no setting, so the spring is drawn at the loosest one
#: the drawing allows, which is the one the design itself draws.
SLACK = (handle_bolt_length - handle_nut_height - SPRING_SEAT
         - m4_washer_thickness - IdlerSpring.free_length)


class Handle(AssemblyNode):
    """The lever, the two long M4 bolts through it, and their springs.

    Each bolt runs from a nut at the handle plate, through the plate,
    across the block, through the idler's back plate and out to its
    head in front of the machine.  Between that plate and the head sits
    the spring, on the washer the bill of materials buys for it, and
    what the spring does is push the top of the idler arm backwards --
    which swings the bearing at the bottom of the arm onto the filament
    and holds it against the hobbed bolt.

    Squeezing the lever works the other way: it drives the bolts
    forward, lets the springs out, and the idler swings clear so
    filament can be pushed in or pulled out.

    The washer under each spring is not decoration: the back plate
    carries a slot rather than a hole -- four millimetres across and
    nine long -- because the bolt has to travel across it as the arm
    swings, and a spring seated straight on a slot would have nothing
    under half of its end coil.

    The two M4 lock nuts each bolt carries are not drawn.  The design
    has a `locknut` module and calls it for M3 and M8 only; there is no
    M4 lock nut anywhere in the sources, and no dimension one could be
    drawn from.
    """

    def __init__(self, *args, **kwargs):
        self.plate = HandlePlate()

        self.bolts = []
        self.spring_washers = []
        self.springs = []

        for side in (-1, 1):
            across = side * HandleWidth / 6

            self.bolts.append(
                Bolt(4, handle_bolt_length).translate(
                    [across, BOLT_ROW,
                     handle_bolt_length - handle_nut_height]))

            self.spring_washers.append(
                M4Washer().translate([across, BOLT_ROW, SPRING_SEAT]))

            spring = IdlerSpring()
            self.springs.append(spring.translate(
                [across + spring.coil_radius, BOLT_ROW,
                 SPRING_SEAT + m4_washer_thickness
                 + spring.wire_diameter / 2]))

        super().__init__(*args, **kwargs)

    def render(self):
        """Tell each spring how long it is standing.

        Its free length, because that is what the design draws: the
        bolt is drawn with its tension nut at the very end of the
        thread, which is the setting that presses the spring least.
        How far in from there a maker winds it is a state the machine
        has and the design never names, and the port is where it would
        arrive.
        """
        for spring in self.springs:
            self.connect(spring.rise, spring.height)

        return ([self.plate] + self.bolts + self.spring_washers
                + self.springs)
