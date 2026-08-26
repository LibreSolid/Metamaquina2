"""The RAMBo board."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import rambo


class RamboPcb(ScadPart):
    """The controller board itself.

    The design draws the bare board -- its outline and its mounting
    holes -- and not the components on it, so that is what this is.
    Not a `SheetPart`: the design never named the board's outline as a
    2D module, so there is no profile to author separately from the
    extrusion.
    """

    color = materials.PCB

    def render(self):
        return rambo.RAMBo_pcb()
