"""The flexible coupling between a Z motor shaft and a Z bar."""

from solid_node.motion.joints import Revolute

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import coupling


class ShaftCoupling(ScadPart):
    """Bought as one piece, so one leaf.

    `spin` needs no anchor: `coupling.scad`'s own `coupling()` module
    is a cylinder at the origin, so turning it about its own placed
    origin is turning it about the shaft it clamps, wherever it stands.
    """

    color = materials.ABS

    spin = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return coupling.coupling()
