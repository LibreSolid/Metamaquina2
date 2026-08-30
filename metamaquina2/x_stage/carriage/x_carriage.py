"""The X carriage."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.double_m3_spacer import DoubleM3Spacer
from metamaquina2.hardware.lm8uu import LM8UU
from metamaquina2.params import (
    XCarPosition,
    XCarriage_height,
    XCarriage_length,
    XCarriage_lm8uu_distance,
    XCarriage_padding,
    XEnd_extra_width,
    XPlatform_width,
    X_rod_height,
    X_rods_distance,
    bearing_sandwich_spacing,
    belt_clamp_height,
    belt_offset,
    belt_width,
    lm8uu_diameter,
    thickness,
)
from metamaquina2.x_stage.carriage.belt_clamp import XBeltClamp
from metamaquina2.x_stage.carriage.carriage_plate import XCarriagePlate
from metamaquina2.x_stage.carriage.extruder.extruder import (
    FILAMENT_ENTRY as ENTRY_ON_THE_EXTRUDER,
    Extruder,
)
from metamaquina2.x_stage.carriage.sandwich_plate import (
    XCarriageSandwichPlate)


#: Where the extruder stands on this carriage: on the plate, at the
#: design's own rest position, and turned to face the front of the
#: machine.  Named because two things read it -- the extruder itself,
#: and the filament that ends inside it.
EXTRUDER_POSITION = [XCarPosition, 0, XCarriage_height + thickness]
EXTRUDER_ANGLE = 90

#: Where the filament goes in, in this carriage's own frame: the
#: extruder's own entry, carried through the quarter turn that faces it
#: forward, which swaps the extruder's x onto the carriage's y.
FILAMENT_ENTRY = [EXTRUDER_POSITION[0] - ENTRY_ON_THE_EXTRUDER[1],
                  EXTRUDER_POSITION[1] + ENTRY_ON_THE_EXTRUDER[0],
                  EXTRUDER_POSITION[2] + ENTRY_ON_THE_EXTRUDER[2]]


class XCarriage(AssemblyNode):
    """What rides the X rods: plate, bearings, belt clamps, extruder.

    Four linear bearings are trapped between the carriage plate and a
    sandwich plate below it, spaced by six pairs of stacked spacers.
    Two clamps grip the belt, one at each end, so the belt pulls the
    carriage both ways.

    The design puts the J-head hot end here, at the carriage rather
    than in the extruder, because it draws it from a file that never
    parsed.  Here it hangs where a builder bolts it, under the extruder
    block; see `jhead`.
    """

    spacer_span = 1.3

    def __init__(self, *args, **kwargs):
        deck = XCarriage_height
        bearing_reach = XCarriage_lm8uu_distance / 2

        self.plate = XCarriagePlate().translate([XCarPosition, 0, deck])

        spacer_deck = deck - bearing_sandwich_spacing
        positions = []
        for side in (-1, 1):
            for edge in (-1, 1):
                positions.append(
                    (side * bearing_reach,
                     edge * (XPlatform_width / 2 - XCarriage_padding)))
            positions.append(
                (side * (XCarriage_length / 2 - XCarriage_padding), 0))
        self.spacers = [
            DoubleM3Spacer().translate([XCarPosition + x, y, spacer_deck])
            for x, y in positions
        ]

        self.sandwich_plate = XCarriageSandwichPlate().translate(
            [XCarPosition, 0, spacer_deck - thickness])

        self.extruder = (Extruder()
                         .rotate(EXTRUDER_ANGLE, [0, 0, 1])
                         .translate(EXTRUDER_POSITION))

        clamp_y = (XPlatform_width / 2 + XEnd_extra_width - belt_offset
                   + belt_width)
        clamp_z = (belt_clamp_height + 2 * thickness + X_rod_height
                   + lm8uu_diameter / 2)
        self.belt_clamps = [
            XBeltClamp(flipped=(side == 1))
            .rotate(180, [1, 0, 0])
            .rotate(90, [0, 0, 1])
            .translate([XCarPosition
                        + side * self.spacer_span * (bearing_reach + 10),
                        clamp_y, clamp_z])
            for side in (-1, 1)
        ]

        rod_deck = thickness + X_rod_height
        self.bearings = [
            LM8UU()
            .rotate(90, [0, 0, 1])
            .translate([XCarPosition + side * bearing_reach,
                        rod * X_rods_distance / 2, rod_deck])
            for side in (-1, 1) for rod in (-1, 1)
        ]

        super().__init__(*args, **kwargs)

    def render(self):
        return ([self.plate] + self.spacers
                + [self.sandwich_plate, self.extruder]
                + self.belt_clamps + self.bearings)
