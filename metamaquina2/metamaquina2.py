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

Where the geometry comes from is in `scad.py`, where the dimensions
come from is in `params.py`, and how a part is authored is in
`part.py`.
"""

from solid_node.node import AssemblyNode

from metamaquina2.electronics.electronics import Electronics
from metamaquina2.frame.frame import Frame
from metamaquina2.params import (
    BuildPlatform_height,
    XZStage_offset,
    ZCarPosition,
    nozzle_tip_distance,
)
from metamaquina2.spool_holder.spool_holder import SpoolHolder
from metamaquina2.x_stage.x_stage import XStage
from metamaquina2.y_axis.y_axis import YAxis
from metamaquina2.z_axis.z_axis import ZAxis


class Metamaquina2(AssemblyNode):
    """The complete Metamaquina 2 desktop 3D printer."""

    # where the stand sits beside the machine
    spool_holder_position = [400, 0, 0]

    def __init__(self, *args, **kwargs):
        self.frame = Frame()

        self.z_axis = ZAxis()
        self.y_axis = YAxis()
        self.x_stage = XStage().translate(
            [0, -XZStage_offset,
             BuildPlatform_height + ZCarPosition + nozzle_tip_distance])

        self.electronics = Electronics()

        self.spool_holder = (SpoolHolder()
                             .rotate(90, [0, 0, 1])
                             .translate(self.spool_holder_position))

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.frame, self.z_axis, self.y_axis, self.x_stage,
                self.electronics, self.spool_holder]
