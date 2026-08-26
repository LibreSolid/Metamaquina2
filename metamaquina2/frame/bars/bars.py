"""The four horizontal threaded bars that hold the frame square."""

from solid_node.node import AssemblyNode

from metamaquina2.frame.bars.front_bars import FrontBars
from metamaquina2.frame.bars.rear_bars import RearBars


class Bars(AssemblyNode):
    """Front and rear bar assemblies.

    These are what actually make the machine rigid: the panels locate
    everything, but it is the bars, pulled up between the side panels,
    that stop the frame racking.
    """

    def __init__(self, *args, **kwargs):
        self.front = FrontBars()
        self.rear = RearBars()
        super().__init__(*args, **kwargs)

    def render(self):
        return [self.front, self.rear]
