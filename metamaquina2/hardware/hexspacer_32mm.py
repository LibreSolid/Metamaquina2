"""32 mm threaded hex spacer."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import spacers


class HexSpacer32mm(ScadPart):
    """The standoff that holds the RAMBo cover off the board."""

    color = materials.METAL

    def render(self):
        return spacers.hexspacer_32mm()
