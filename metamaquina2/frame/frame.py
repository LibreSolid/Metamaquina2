"""The frame: panels, the bolts that join them, and the bars."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.bars.bars import Bars
from metamaquina2.frame.joints import PanelJoints
from metamaquina2.frame.panels.panels import Panels


class Frame(AssemblyNode):
    """Everything a builder puts together before any axis exists.

    Five panels bolted to each other through t-slots, four threaded
    bars pulling the sides together, and the rod-end plates that will
    take the Z axis.

    Each part of it already stands where it belongs in the machine's
    own frame, so there is nothing here to position.
    """

    panels = Panels()
    joints = PanelJoints()
    bars = Bars()
