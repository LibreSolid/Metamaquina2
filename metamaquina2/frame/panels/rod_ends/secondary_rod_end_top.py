"""The reinforcing plate under each upper rod end."""

from metamaquina2.part import SheetPart
from metamaquina2.scad import machine


class SecondaryRodEndTop(SheetPart):
    """A second, shorter plate below the top panel that doubles up the
    upper rod end."""

    def profile(self):
        return machine.SecondaryRodEndTop_face()
