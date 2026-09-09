"""The Z axis."""

from solid_node.node import AssemblyNode

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

    How far the bars have been turned reaches `bars.angle` and
    `couplings.angle` by path from the machine, one for one -- a
    coupling is clamped to the shaft it joins, so there is no ratio
    between them to state.  The motors and the smooth rods take
    nothing: a stepper's case does not turn with its rotor, and a rod
    the stage slides on never did.

    Nothing here is placed: each of the four stands in the machine's
    own frame already, so there is nothing for `render` to do, and this
    axis has nothing left to say per instant either.
    """

    motors = ZMotors()
    couplings = ZCouplings()
    bars = ZBars()
    rods = ZRods()
