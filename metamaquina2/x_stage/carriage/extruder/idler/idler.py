"""The extruder idler arm."""

from solid_node.node import AssemblyNode

from metamaquina2.hardware.bearing_608zz import Bearing608zz
from metamaquina2.params import (
    bearing_thickness,
    idler_axis_position,
    idler_bearing_position,
    idler_radius,
    thickness,
)
from metamaquina2.x_stage.carriage.extruder.idler.axle import IdlerAxle
from metamaquina2.x_stage.carriage.extruder.idler.back_plate import (
    IdlerBackPlate)
from metamaquina2.x_stage.carriage.extruder.idler.side_plate import (
    IdlerSidePlate)
from metamaquina2.x_stage.carriage.extruder.idler.spacer import IdlerSpacer


class Idler(AssemblyNode):
    """The arm that presses filament onto the hobbed bolt.

    Two side plates and a back plate make a U; a 608 bearing on a short
    axle runs between the side plates and bears on the filament.  The
    small gaps in the stack -- half a millimetre here, a millimetre
    there -- are the design's allowance for how much lasercut and
    acrylic thickness actually vary.

    Drawn in the extruder's own flat plane; the extruder stands it up.
    """

    # the design's slack for real sheet thickness
    plate_clearance = 0.5
    spacer_clearance = 1.0

    # Where the back plate's outer face stands, in the extruder's own
    # flat frame: a radius out from the pivot, which is where the notch
    # cut into each side plate seats it.  The handle's two long bolts
    # pass through this plate, and their springs stand on this face --
    # the far one, so that compressing a spring swings the arm shut on
    # the filament rather than open.
    back_face = idler_axis_position[0] - idler_radius

    def __init__(self, *args, **kwargs):
        axis_x, axis_y = idler_axis_position
        bearing_x, bearing_y = idler_bearing_position

        self.axle = (IdlerAxle()
                     .translate([0, 0, -IdlerAxle.length])
                     .translate([bearing_x, bearing_y, 5 * thickness]))

        def on_arm(node):
            """Into the arm's own frame, at the pivot."""
            return node.translate([axis_x, axis_y, 0])

        self.lower_side = on_arm(IdlerSidePlate())
        self.upper_side = on_arm(
            IdlerSidePlate().translate([0, 0, 4 * thickness]))

        def in_bearing_stack(node, height):
            return on_arm(
                node
                .translate([0, 0, thickness + self.plate_clearance + height])
                .translate([bearing_x - axis_x, bearing_y - axis_y, 0]))

        stack = thickness - self.spacer_clearance
        self.lower_spacer = in_bearing_stack(IdlerSpacer(), 0)
        self.bearing = in_bearing_stack(Bearing608zz(), stack)
        self.upper_spacer = in_bearing_stack(
            IdlerSpacer(), stack + bearing_thickness)

        self.back_plate = on_arm(
            IdlerBackPlate()
            .rotate(-90, [0, 1, 0])
            .translate([-idler_radius + thickness, idler_radius,
                        5 * thickness / 2]))

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.axle, self.lower_side, self.upper_side,
                self.lower_spacer, self.bearing, self.upper_spacer,
                self.back_plate]
