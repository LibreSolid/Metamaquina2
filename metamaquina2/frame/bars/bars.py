"""The four horizontal threaded bars that hold the frame square."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.bars.front_bars import FrontBars
from metamaquina2.frame.bars.rear_bars import RearBars


class Bars(AssemblyNode):
    """Front and rear bar assemblies.

    These are what actually make the machine rigid: the panels locate
    everything, but it is the bars, pulled up between the side panels,
    that stop the frame racking.

    Nothing to position: the two halves stand in the machine's own
    frame, so the class body is the whole assembly.
    """

    front = FrontBars()
    rear = RearBars()
