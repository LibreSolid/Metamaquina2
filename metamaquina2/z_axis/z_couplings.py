"""The couplings that join each Z motor shaft to its threaded bar."""

from solid_node.motion.ports import RotationalPort
from solid_node.node import AssemblyNode

from metamaquina2.hardware.shaft_coupling import ShaftCoupling
from metamaquina2.params import (
    BottomPanel_zoffset,
    XZStage_offset,
    coupling_shaft_depth,
    lm8uu_diameter,
    machine_x_dim,
    motor_shaft_length,
    thickness,
    z_rod_z_bar_distance,
)


class ZCouplings(AssemblyNode):
    """Two flexible couplings, one per side.

    They sit where the motor shaft ends and the threaded bar begins,
    and they are what lets the bar be slightly out of true with the
    motor without binding the axis.

    They also turn, which is the plainest thing about them and was
    missing: a coupling is clamped to the shaft at one end and to the
    bar at the other, so it goes round with both or it is not a
    coupling.  `angle` is the bar's own, relayed by the axis -- `angle`
    drives `couplings.spin` once, fanned out over both copies -- and
    there is nothing for this assembly to derive from it, because a
    clamped joint has no ratio.

    Where each coupling sits is fixed by the shaft and the bar it
    clamps, so `render` seats the two of them once and there is
    nothing left to say per instant: each coupling's own `spin` joint
    turns it about its own axis, wherever `render` has translated it.
    """

    angle = RotationalPort(unit='deg')

    offset = (machine_x_dim / 2 - thickness - lm8uu_diameter / 2
              - z_rod_z_bar_distance)
    height = (BottomPanel_zoffset + motor_shaft_length
              - coupling_shaft_depth)

    couplings = ShaftCoupling().repeat(2)

    angle.drives(couplings.spin)

    def render(self):
        for side, coupling in zip((-1, 1), self.couplings):
            coupling.translate(
                [side * self.offset, -XZStage_offset, self.height])
