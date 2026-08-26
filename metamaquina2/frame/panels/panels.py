"""Every lasercut panel of the frame, standing where it belongs."""

from solid_node.node import AssemblyNode

from metamaquina2 import frames
from metamaquina2.frame.panels.arc_panel import ArcPanel
from metamaquina2.frame.panels.bottom_panel import BottomPanel
from metamaquina2.frame.panels.left_panel import LeftPanel
from metamaquina2.frame.panels.right_panel import RightPanel
from metamaquina2.frame.panels.rod_ends.rod_ends import RodEnds
from metamaquina2.frame.panels.top_panel import TopPanel
from metamaquina2.frame.panels.wiring_hole_ring import WiringHoleRing
from metamaquina2.params import thickness


class Panels(AssemblyNode):
    """The five big panels, the two wiring rings and the rod ends.

    The panels are separate parts that a builder bolts together, not
    one welded shell, so this is an assembly and each panel is its own
    leaf.  What holds them together is in `PanelJoints`.
    """

    # where the wiring rings sit in the top panel's plane
    wiring_hole_offset = 120

    def __init__(self, *args, **kwargs):
        self.left = frames.left_panel(LeftPanel())
        self.right = frames.right_panel(RightPanel())
        self.top = frames.top_panel(TopPanel())
        self.bottom = frames.bottom_panel(BottomPanel())
        self.arc = frames.arc_panel(ArcPanel())

        self.wiring_ring_above = frames.top_panel(
            WiringHoleRing().translate(
                [0, self.wiring_hole_offset, thickness]))
        self.wiring_ring_below = frames.top_panel(
            WiringHoleRing().translate(
                [0, self.wiring_hole_offset, -thickness]))

        self.rod_ends = RodEnds()

        super().__init__(*args, **kwargs)

    def render(self):
        return [self.left, self.right, self.top, self.bottom, self.arc,
                self.wiring_ring_above, self.wiring_ring_below,
                self.rod_ends]
