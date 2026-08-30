"""The Z axis."""

from solid_node.node import AssemblyNode, RotationalPort

from metamaquina2.z_axis.z_bars import ZBars
from metamaquina2.z_axis.z_couplings import ZCouplings
from metamaquina2.z_axis.z_motors import ZMotors
from metamaquina2.z_axis.z_rods import ZRods


class ZAxis(AssemblyNode):
    """Motors, couplings, threaded bars and smooth rods.

    The X stage rides this: two bearings per side on the smooth rods
    carry it, and a nut in each Z link, driven by a threaded bar,
    raises it.  Two independent motors, which is why the machine can
    be levelled but also why it can be racked.

    `screw` is how far the bars have been turned, and it goes to the
    bars and to the couplings alike -- a coupling is clamped to the
    shaft it joins, so there is no ratio between them to state.  The
    motors and the smooth rods take nothing: a stepper's case does not
    turn with its rotor, and a rod the stage slides on never did.
    """

    screw = RotationalPort(unit='deg')

    def __init__(self, *args, **kwargs):
        self.motors = ZMotors()
        self.couplings = ZCouplings()
        self.bars = ZBars()
        self.rods = ZRods()
        super().__init__(*args, **kwargs)

    def render(self):
        self.connect(self.screw, self.bars.angle)
        self.connect(self.screw, self.couplings.angle)

        return [self.motors, self.couplings, self.bars, self.rods]
