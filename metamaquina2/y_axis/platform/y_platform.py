"""The moving Y platform: the bed carriage."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.double_m3_spacer import DoubleM3Spacer
from metamaquina2.hardware.lm8uu import LM8UU
from metamaquina2.params import (
    YEndstopHolder_distance,
    YPlatform_zoffset,
    Y_rods_distance,
    bearing_sandwich_spacing,
    lm8uu_diameter,
    pcb_height,
    thickness,
)
from metamaquina2.y_axis.heated_bed.heated_bed import HeatedBed
from metamaquina2.y_axis.platform.belt_clamp import YBeltClamp
from metamaquina2.y_axis.platform.endstop_holder import YEndstopHolder
from metamaquina2.y_axis.platform.left_sandwich import LeftBearingSandwich
from metamaquina2.y_axis.platform.platform_plate import YPlatformPlate
from metamaquina2.y_axis.platform.right_sandwich import RightBearingSandwich
from metamaquina2.y_axis.platform.sandwich_bolt import SandwichBolt


class YPlatform(AssemblyNode):
    """Everything that travels with the bed.

    One plate, three linear bearings trapped under it by two sandwich
    plates, the spacers that set the gap, four belt clamps, two endstop
    tabs and the heated bed on top.

    Three bearings, not four: one on the left rod and two on the right.
    That is the design's choice and it is what makes the platform
    kinematically determinate instead of fighting itself when the rods
    are not perfectly parallel.

    The platform is drawn where it sits at the middle of its travel;
    the Y axis moves it.
    """

    # where the belt clamps grip, either side of the centreline
    belt_clamp_offsets = (-20, 20)
    # the gap the second belt clamp of each pair leaves for the belt
    belt_gap = 3
    # the sandwich bolt patterns, in each sandwich's own plane
    left_bolt_holes = ((14, 20), (14, -20), (-14, 0))
    right_bolt_holes = ((14, 50), (14, -50), (-14, 50), (-14, -50))

    def __init__(self, *args, **kwargs):
        deck = YPlatform_zoffset
        left = -Y_rods_distance / 2
        right = Y_rods_distance / 2

        self.heated_bed = HeatedBed().translate([0, 0, pcb_height])
        self.plate = YPlatformPlate().translate([0, 0, deck])

        self.belt_clamps = []
        for offset in self.belt_clamp_offsets:
            self.belt_clamps.append(
                YBeltClamp().translate([0, offset, deck - thickness]))
            self.belt_clamps.append(
                YBeltClamp().translate(
                    [0, offset, deck - 2 * thickness - self.belt_gap]))

        spacer_deck = deck - bearing_sandwich_spacing
        spacer_positions = [(left - 14, 0)]
        spacer_positions += [(left + 14, side * 20) for side in (-1, 1)]
        spacer_positions += [(right + side * 14, corner * 50)
                             for side in (-1, 1) for corner in (-1, 1)]
        self.spacers = [
            DoubleM3Spacer().translate([x, y, spacer_deck])
            for x, y in spacer_positions
        ]

        sandwich_deck = spacer_deck - thickness
        self.left_sandwich = LeftBearingSandwich().translate(
            [left, 0, sandwich_deck])
        self.left_bolts = [
            SandwichBolt()
            .rotate(180, [1, 0, 0])
            .translate([left + x, y, sandwich_deck])
            for x, y in self.left_bolt_holes
        ]

        self.right_sandwich = RightBearingSandwich().translate(
            [right, 0, sandwich_deck])
        self.right_bolts = [
            SandwichBolt()
            .rotate(180, [1, 0, 0])
            .translate([right + x, y, sandwich_deck])
            for x, y in self.right_bolt_holes
        ]

        bearing_deck = deck - lm8uu_diameter / 2
        self.bearings = [LM8UU().translate([left, 0, bearing_deck])]
        self.bearings += [
            LM8UU().translate([right, side * 50, bearing_deck])
            for side in (-1, 1)
        ]

        self.endstop_holders = [
            YEndstopHolder()
            .rotate(-90, [1, 0, 0])
            .translate([YEndstopHolder_distance / 2, 90, deck]),
            YEndstopHolder()
            .rotate(-90, [1, 0, 0])
            .translate([-YEndstopHolder_distance / 2, -90 - thickness, deck]),
        ]

        super().__init__(*args, **kwargs)

    def render(self):
        return ([self.heated_bed, self.plate]
                + self.belt_clamps
                + self.spacers
                + [self.left_sandwich] + self.left_bolts
                + [self.right_sandwich] + self.right_bolts
                + self.bearings
                + self.endstop_holders)
