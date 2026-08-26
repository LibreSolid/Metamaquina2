"""An acrylic spacer that stands a Z endstop off the side panel."""

from metamaquina2 import materials
from metamaquina2.part import SheetPart
from metamaquina2.params import acrylic_thickness
from metamaquina2 import scad


class ZEndstopSpacer(SheetPart):
    """One of four different spacer profiles: two under the Z minimum
    switch and two under the Z maximum switch.

    Each pair is a different shape, so the switch ends up square to the
    Z rod and its wire has somewhere to leave.  The `kind` names which
    profile is cut.
    """

    kinds = ('zmin1', 'zmin2', 'zmax1', 'zmax2')

    color = materials.ACRYLIC
    sheet_thickness = acrylic_thickness

    def __init__(self, kind, **kwargs):
        if kind not in self.kinds:
            raise ValueError(
                f'no such Z endstop spacer {kind!r}; '
                f'expected one of {", ".join(self.kinds)}')
        self.kind = kind
        super().__init__(kind, **kwargs)

    def profile(self):
        name = f'{self.kind[:4]}_endstop_spacer_face{self.kind[4:]}'
        return getattr(scad.endstop, name)()
