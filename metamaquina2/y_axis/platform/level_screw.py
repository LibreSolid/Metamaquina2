"""One corner of the heated bed's levelling."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bolt import Bolt
from metamaquina2.hardware.m3_nut import M3Nut
from metamaquina2.hardware.m3_washer import M3Washer
from metamaquina2.params import (
    heated_bed_pcb_thickness,
    m3_nut_height,
    m3_washer_thickness,
    thickness,
)
from metamaquina2.y_axis.platform.bed_spring import INSTALLED, SEAT, BedSpring


class BedLevelScrew(AssemblyNode):
    """The bolt, the spring and the nut that hold one corner of the bed.

    The bolt drops through the corner hole in the bed board, through
    the spring, through the same hole in the platform sheet below, and
    a nut under the sheet pulls the corner down against the spring.
    Four of these are how the bed is levelled, and they are the reason
    the bed is sprung at all.

    Drawn from the platform sheet's top face, because that is the one
    surface everything here is measured from: the spring stands on it,
    the board floats `SEAT` above it, and the nut hangs a sheet's
    thickness below it.

    The bill of materials buys a wing nut for the job -- ``Borboleta
    M3``, which is what a hand turns without a spanner -- and the design
    draws no wing nut anywhere, nor gives a dimension one could be drawn
    from.  So the plain M3 hex nut the design does draw stands in for
    it, and that is a departure rather than a reading: the part on the
    machine has wings.
    """

    #: What the bill of materials buys to hold each corner.
    bolt_length = 30

    def __init__(self, *args, **kwargs):
        spring = BedSpring()
        self.spring = spring.translate(
            [spring.coil_radius, 0, spring.wire_diameter / 2])

        # Under the board, spreading the spring's end coil over the
        # copper rather than letting it press into it.
        self.seat_washer = M3Washer().translate([0, 0, INSTALLED])

        # On top of the board, under the head. The corner holes are at
        # y = +/-107 and the glass reaches only +/-100, so the head sits
        # on bare board and the glass comes off past it.
        head_seat = SEAT + heated_bed_pcb_thickness
        self.head_washer = M3Washer().translate([0, 0, head_seat])
        self.bolt = Bolt(3, self.bolt_length).translate(
            [0, 0, head_seat + m3_washer_thickness])

        # Under the platform sheet, and the nut under that.
        nut_seat = -thickness - m3_washer_thickness
        self.nut_washer = M3Washer().translate([0, 0, nut_seat])
        self.nut = M3Nut().translate([0, 0, nut_seat - m3_nut_height])

        super().__init__(*args, **kwargs)

    def render(self):
        """Tell the spring how much room it has been left.

        A constant today, and deliberately: the length is derived from
        where this package puts the board and the platform, so turning
        the bed's level into something a maker drives would move
        `BuildPlatform_height`, which is where the Z axis is measured
        from.  That is a change to the machine's motion rather than to
        its parts.  The port is here so that when it is made, it is a
        wire and not a redrawing.
        """
        self.connect(self.spring.rise, self.spring.height)

        return [self.spring, self.seat_washer, self.head_washer, self.bolt,
                self.nut_washer, self.nut]
