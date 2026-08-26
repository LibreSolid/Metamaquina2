"""A lasercut clamp that grips the Y belt under the platform."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import belt_clamp


class YBeltClamp(SheetPart):
    """One of four plates; two stacked at each end of the belt run,
    pinching the belt between them."""

    width = 28
    radius = 5

    def profile(self):
        return belt_clamp.beltclamp_curves(
            self.width, self.radius, for_y_platform=True)
