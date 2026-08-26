"""608ZZ ball bearing."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import call


class Bearing608zz(ScadPart):
    """The skate bearing used as an idler on every belt.

    Its OpenSCAD module is named `608zz_bearing`, which is not a Python
    identifier, so it is called by name rather than as an attribute of
    the imported source.
    """

    color = materials.METAL

    def render(self):
        return call('608zz_bearing', details=True)
