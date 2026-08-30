"""The Metamaquina 2, as an assembly.

The machine is designed in OpenSCAD, in the .scad files beside this
package, and that design is left exactly as it is.  What this package
adds is a second reading of it: a tree of nodes in which every part a
builder handles -- every plate that gets cut, every bolt that gets
turned, every bearing that gets pressed -- is a leaf, and every group
that gets put together before it goes into something bigger is an
assembly.

The tree follows the build, not the source file.  A frame first,
because nothing can be fitted until the panels and bars are square.
Then the three axes, each with its own rods, its own drive, and the
thing it moves.  Then the electronics, which go on last.  The spool
holder is a separate stand and hangs off the root beside the machine,
which is where the design draws it.

The design already had a knob for each axis -- `XCarPosition`,
`YCarPosition` and `ZCarPosition`, the three numbers that decide where
the .scad file draws a machine at rest.  Here they are drivers instead:
the same coordinates, with the same numbers as defaults, but read at
every render rather than baked in once.  So the machine that opens is
the machine that has always been drawn, and it can now be sent
somewhere else without editing anything.

What moves is what carries the print: the carriage along the X beam,
the bed along its rods, the whole X beam up and down the Z rods.  One
thing turns with them, and only one: the pulley the X belt is meshed
on, because a groove has to stay under every tooth that comes round to
it and the belt says exactly where.  The Z screws and the other two
motors stand still, which is a stopping point rather than an oversight
-- a screw that turns needs a rotation nothing in the design pins
down, and nothing about where the machine is depends on it.

The two belts used to stand still for a different and worse reason.  A
belt does not go anywhere: both ends of each loop are bolted down, and
the loop keeps its shape from one end of the travel to the other.  But
it is not still either -- the rubber inside the loop is dragged through
it by the carriage clamped to it, so a belt is a shape to be re-drawn
at every position rather than a part to be re-placed, and the design's
2 mm ring hulled around a few circles has nowhere to put a tooth.  Both
belts are now what they are on the machine: GT2, toothed, clamped to
the thing they pull, drawn afresh from wherever that thing is.  Both
motors that drive one have the pulley the design's own bill of
materials buys and its module never drew, and the X one is meshed:
what a GT2 belt and its pulley are lives in `gt2.py`, the part is in
`hardware/gt2_pulley.py`, and the loops themselves are in
`x_stage/x_belt.py` and `y_axis/y_belt.py`.

Where the geometry comes from is in `scad.py`, where the dimensions
come from is in `params.py`, and how a part is authored is in
`part.py`.
"""

from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, Instruction

from metamaquina2.electronics.electronics import Electronics
from metamaquina2.frame.frame import Frame
from metamaquina2.params import (
    BuildPlatform_height,
    BuildVolume_X,
    BuildVolume_Y,
    BuildVolume_Z,
    XCarPosition,
    XZStage_offset,
    YCarPosition,
    ZCarPosition,
    nozzle_tip_distance,
)
from metamaquina2.spool_holder.spool_holder import SpoolHolder
from metamaquina2.x_stage.x_stage import XStage
from metamaquina2.y_axis.y_axis import YAxis
from metamaquina2.z_axis.z_axis import ZAxis


class Metamaquina2(AssemblyNode):
    """The complete Metamaquina 2 desktop 3D printer.

    The three drivers are declared here, on the machine, rather than
    one per axis, because that is where a maker meets them: the
    coordinates on the panel of a printer are the printer's, not the
    X carriage's opinion of its own beam.  Each one is a position in
    millimetres in the design's own coordinates, which is what makes
    `XCarPosition` a default and not a conversion.

    The travel each declares is the build volume the machine
    advertises: X and Y reach half of it either side of centre, and Z
    counts the nozzle up from the bed to the full height.
    """

    # where the stand sits beside the machine
    spool_holder_position = [400, 0, 0]

    x = Driver(default=XCarPosition, unit='mm',
               range=(-BuildVolume_X / 2, BuildVolume_X / 2))
    y = Driver(default=YCarPosition, unit='mm',
               range=(-BuildVolume_Y / 2, BuildVolume_Y / 2))
    z = Driver(default=ZCarPosition, unit='mm',
               range=(0, BuildVolume_Z))

    instructions = {
        # Back to the pose the design draws, all three axes at once.
        'Home': Instruction({'x': XCarPosition,
                             'y': YCarPosition,
                             'z': ZCarPosition}, duration=4.0),
        # The carriage crosses to the middle of the bed.
        'CenterX': Instruction({'x': 0.0}, duration=2.0),
        # The bed comes forward, out from under the arc panel at the
        # back, which is how a finished print is reached.
        'PresentBed': Instruction({'y': -BuildVolume_Y / 2}, duration=2.0),
        # The nozzle comes all the way down to the build surface.
        'LowerZ': Instruction({'z': 0.0}, duration=3.0),
    }

    def __init__(self, *args, **kwargs):
        self.frame = Frame()

        self.z_axis = ZAxis()
        self.y_axis = YAxis()
        self.x_stage = XStage()

        self.electronics = Electronics()

        self.spool_holder = (SpoolHolder()
                             .rotate(90, [0, 0, 1])
                             .translate(self.spool_holder_position))

        super().__init__(*args, **kwargs)

    def render(self):
        """Place what the drivers move, then hand over the children.

        X and Y are relayed into the axis that owns the moving frame,
        because the carriage and the bed are placed inside their own
        assemblies.  Z is not: the machine itself is what holds the X
        stage at a height, so the lift is this translate and no port is
        needed for it.
        """
        self.connect(self.x, self.x_stage.carriage_position)
        self.connect(self.y, self.y_axis.platform_position)

        self.x_stage.translate(
            [0, -XZStage_offset,
             BuildPlatform_height + self.z + nozzle_tip_distance])

        return [self.frame, self.z_axis, self.y_axis, self.x_stage,
                self.electronics, self.spool_holder]
