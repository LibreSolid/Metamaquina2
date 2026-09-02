"""A lasercut clamp that grips the Y belt under the platform."""

from solid_node.node import Length

from metamaquina2.part import SheetPart
from metamaquina2.scad import belt_clamp


class YBeltClamp(SheetPart):
    """One of four plates; two stacked at each end of the belt run,
    pinching the belt between them."""

    width = Length(28.0, min=0)
    radius = Length(5.0, min=0)

    def profile(self):
        return belt_clamp.beltclamp_curves(
            self.width, self.radius, for_y_platform=True)
