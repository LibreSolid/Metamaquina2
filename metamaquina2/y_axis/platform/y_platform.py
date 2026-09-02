"""The moving Y platform: the bed carriage."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.double_m3_spacer import DoubleM3Spacer
from metamaquina2.hardware.lm8uu import LM8UU
from metamaquina2.params import (
    YEndstopHolder_distance,
    YPlatform_zoffset,
    Y_rods_distance,
    bearing_sandwich_spacing,
    heated_bed_hole_border,
    heated_bed_pcb_height,
    heated_bed_pcb_width,
    lm8uu_diameter,
    pcb_height,
    thickness,
)
from metamaquina2.y_axis.heated_bed.heated_bed import HeatedBed
from metamaquina2.y_axis.platform.belt_clamp import YBeltClamp
from metamaquina2.y_axis.platform.endstop_holder import YEndstopHolder
from metamaquina2.y_axis.platform.left_sandwich import LeftBearingSandwich
from metamaquina2.y_axis.platform.level_screw import BedLevelScrew
from metamaquina2.y_axis.platform.platform_plate import YPlatformPlate
from metamaquina2.y_axis.platform.right_sandwich import RightBearingSandwich
from metamaquina2.y_axis.platform.sandwich_bolt import SandwichBolt


#: The bolt patterns of the two bearing sandwiches, each in its own
#: plane, and where the spacers that set their gaps stand.
LEFT_BOLT_HOLES = ((14, 20), (14, -20), (-14, 0))
RIGHT_BOLT_HOLES = ((14, 50), (14, -50), (-14, 50), (-14, -50))


def _spacer_positions():
    """Where every pair of stacked spacers stands, across the platform.

    One behind the left bearing and two beside it, then four around the
    right-hand pair -- the same five points the design's own sandwiches
    are bolted at.
    """
    left = -Y_rods_distance / 2
    right = Y_rods_distance / 2
    positions = [(left - 14, 0)]
    positions += [(left + 14, side * 20) for side in (-1, 1)]
    positions += [(right + side * 14, corner * 50)
                  for side in (-1, 1) for corner in (-1, 1)]
    return positions


SPACER_POSITIONS = _spacer_positions()


class YPlatform(AssemblyNode):
    """Everything that travels with the bed.

    One plate, three linear bearings trapped under it by two sandwich
    plates, the spacers that set the gap, four belt clamps, two endstop
    tabs, and the heated bed standing on four springs on top.

    The bed does not sit on the plate: it floats above it on the four
    levelling screws, which is how a bed gets level on a machine whose
    platform was cut by a laser.  The plate is cut from the board's own
    outline -- `YPlatform_face` differences its cuts out of
    `heated_bed_pcb_curves` -- so the four corner holes go through both
    sheets at once and the screws stand on the pattern they share.

    Three bearings, not four: one on the left rod and two on the right.
    That is the design's choice and it is what makes the platform
    kinematically determinate instead of fighting itself when the rods
    are not perfectly parallel.

    The platform is drawn where it sits at the middle of its travel;
    the Y axis moves it.

    Everything that appears more than once here is one part repeated:
    four levelling screws, four belt clamps, five pairs of spacers,
    three bearings, seven sandwich bolts and two endstop tabs.
    """

    # where the belt clamps grip, either side of the centreline
    belt_clamp_offsets = (-20, 20)
    # the gap the second belt clamp of each pair leaves for the belt
    belt_gap = 3
    # the sandwich bolt patterns, in each sandwich's own plane
    left_bolt_holes = LEFT_BOLT_HOLES
    right_bolt_holes = RIGHT_BOLT_HOLES

    heated_bed = HeatedBed()
    plate = YPlatformPlate()
    level_screws = BedLevelScrew().repeat(4)
    belt_clamps = YBeltClamp().repeat(2 * len(belt_clamp_offsets))
    spacers = DoubleM3Spacer().repeat(len(SPACER_POSITIONS))
    left_sandwich = LeftBearingSandwich()
    left_bolts = SandwichBolt().repeat(len(LEFT_BOLT_HOLES))
    right_sandwich = RightBearingSandwich()
    right_bolts = SandwichBolt().repeat(len(RIGHT_BOLT_HOLES))
    bearings = LM8UU().repeat(3)
    endstop_holders = YEndstopHolder().repeat(2)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        deck = YPlatform_zoffset
        left = -Y_rods_distance / 2
        right = Y_rods_distance / 2

        self.heated_bed.translate([0, 0, pcb_height])
        self.plate.translate([0, 0, deck])

        corners = [(across, along)
                   for across in (-1, 1) for along in (-1, 1)]
        for screw, (across, along) in zip(self.level_screws, corners):
            screw.translate(
                [across * (heated_bed_pcb_width / 2 - heated_bed_hole_border),
                 along * (heated_bed_pcb_height / 2 - heated_bed_hole_border),
                 deck + thickness])

        clamps = iter(self.belt_clamps)
        for offset in self.belt_clamp_offsets:
            next(clamps).translate([0, offset, deck - thickness])
            next(clamps).translate(
                [0, offset, deck - 2 * thickness - self.belt_gap])

        spacer_deck = deck - bearing_sandwich_spacing
        for spacer, (x, y) in zip(self.spacers, SPACER_POSITIONS):
            spacer.translate([x, y, spacer_deck])

        sandwich_deck = spacer_deck - thickness
        self.left_sandwich.translate([left, 0, sandwich_deck])
        for bolt, (x, y) in zip(self.left_bolts, self.left_bolt_holes):
            (bolt
             .rotate(180, [1, 0, 0])
             .translate([left + x, y, sandwich_deck]))

        self.right_sandwich.translate([right, 0, sandwich_deck])
        for bolt, (x, y) in zip(self.right_bolts, self.right_bolt_holes):
            (bolt
             .rotate(180, [1, 0, 0])
             .translate([right + x, y, sandwich_deck]))

        bearing_deck = deck - lm8uu_diameter / 2
        self.bearings[0].translate([left, 0, bearing_deck])
        for bearing, side in zip(self.bearings[1:], (-1, 1)):
            bearing.translate([right, side * 50, bearing_deck])

        (self.endstop_holders[0]
         .rotate(-90, [1, 0, 0])
         .translate([YEndstopHolder_distance / 2, 90, deck]))
        (self.endstop_holders[1]
         .rotate(-90, [1, 0, 0])
         .translate([-YEndstopHolder_distance / 2, -90 - thickness, deck]))
