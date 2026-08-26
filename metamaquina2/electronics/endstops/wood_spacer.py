"""A lasercut spacer that stands a Y endstop off the bottom panel."""

from metamaquina2.part import SheetPart
from metamaquina2 import scad


class YEndstopSpacer(SheetPart):
    """One of two profiles, one per Y endstop.  Two of the same one
    are stacked under each switch."""

    kinds = ('ymin', 'ymax')

    def __init__(self, kind, **kwargs):
        if kind not in self.kinds:
            raise ValueError(
                f'no such Y endstop spacer {kind!r}; '
                f'expected one of {", ".join(self.kinds)}')
        self.kind = kind
        super().__init__(kind, **kwargs)

    def profile(self):
        return getattr(scad.endstop, f'{self.kind}_endstop_spacer_face')()
