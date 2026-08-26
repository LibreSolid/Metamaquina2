"""The two shapes a part takes in this layer.

Every leaf in the tree is one part of the machine and its geometry
comes from the OpenSCAD design, so every leaf shares two things: it
depends on the whole .scad source set, and it renders one OpenSCAD
expression.  Those live here rather than being repeated in a hundred
files.

`ScadPart` is the general case: implement `render()` and return the
call.  `SheetPart` is the case that dominates this machine, a piece cut
from flat stock -- the design authors those as a 2D ``*_face()`` module
and extrudes it, so the node authors the profile and inherits the
extrusion.  Neither is a node the project instantiates; both are bases.
"""

from solid2.core.object_base import OpenSCADObject
from solid_node.node import Solid2Node

from metamaquina2 import materials
from metamaquina2.params import thickness
from metamaquina2.scad import scad_sources


# The curve resolution the design asks for, from `render.h`.
#
# A part drawn by an OpenSCAD module already gets these: `render.h` is
# `include`d into the file that defines the module, so they are in that
# file's scope wherever the module is called from.  A part drawn here,
# in Python, is not -- it is emitted into the generated file, which has
# no such scope, and comes out at OpenSCAD's much coarser defaults: an
# 8 mm rod becomes a 13-sided prism instead of a 51-sided one.  So the
# few primitives this layer draws itself state the resolution on the
# call.
FACET_ANGLE = 0.01
FACET_SIZE = 0.5


def curve(primitive, **parameters):
    """A curved primitive drawn here, at the design's own resolution."""
    return OpenSCADObject(
        primitive,
        dict(parameters, **{'$fa': FACET_ANGLE, '$fs': FACET_SIZE}))


class ScadPart(Solid2Node):
    """A part whose geometry is one OpenSCAD module of the design.

    The framework invalidates a node from the Python files it imports,
    which here decide only where a part goes, never what it is.  The
    .scad sources decide that, and no Python import mentions them, so
    each part adds them to its own source set: without this a part
    would report itself up to date after an edit to the module that
    draws it.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files = self.files | scad_sources()


class SheetPart(ScadPart):
    """A part cut from flat stock, as a profile and a thickness.

    The design draws each of these as a 2D ``*_face()`` module and
    extrudes it by the stock thickness at the point of use.  Here the
    profile is the part's own declaration and the extrusion follows
    from `sheet_thickness`, so the two cannot be written down
    inconsistently.

    This is not the framework's `Build123dSheetNode` -- the profile is
    OpenSCAD, so there is no exact kernel behind it and no DXF falls
    out.  The intent is the same: the part is authored once, as the
    profile that gets cut.
    """

    color = materials.SHEET
    sheet_thickness = thickness

    def profile(self):
        """The 2D outline this part is cut from."""
        raise NotImplementedError(
            f'{self.__class__.__name__} must implement profile()')

    def render(self):
        return self.profile().linear_extrude(self.sheet_thickness)
