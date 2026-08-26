"""Access to the original OpenSCAD design.

The Metamaquina 2 is authored in OpenSCAD.  This package does not
replace those sources: it is a parallel structure that reads them.
Every leaf node's geometry is one OpenSCAD module, reached through
solid2's ``import_scad``, which emits ``use <absolute path>`` so the
relative ``include``/``use`` chains inside the design keep resolving
from the source directory.

``OpenScadNode`` is deliberately not used anywhere here: that adapter
inlines the .scad text into the generated file under ``_build``, where
none of those relative includes resolve.

Two services live here:

* the imported handles for each source file, one attribute per file;
* :func:`scad_sources`, the set of .scad and .h files the whole design
  is built from, which every node adds to its own source set.  The
  framework's import walk sees Python only, so without this a node
  would report itself up to date after an edit to any part file.
"""

import os

from solid2 import import_scad
from solid2.core.object_base import OpenSCADObject


SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def _handle(filename):
    return import_scad(os.path.join(SOURCE_DIR, filename))


# The machine itself, and the libraries it is built from.  Two module
# names collide across the design -- `M3_hole` (utils.scad and
# lasercut_extruder.scad) and `hobbed_bolt` (hobbed_bolt.scad and
# lasercut_extruder.scad).  solid2 emits one `use` header for every
# file imported anywhere in the process, and OpenSCAD resolves a
# top-level call to the last definition it saw, so the losing file of
# each pair is simply not imported.  Neither is needed: `M3_hole` is a
# 2D helper no node calls directly, and the extruder's own
# `hobbed_bolt` is the one the extruder assembles.
machine = _handle('Metamaquina2.scad')

nuts = _handle('nuts.scad')
bolts = _handle('bolts.scad')
washers = _handle('washers.scad')
spacers = _handle('spacer.scad')
domed_cap_nuts = _handle('domed_cap_nuts.scad')

lm8uu = _handle('lm8uu_bearing.scad')
ball_bearing = _handle('608zz_bearing.scad')
nema = _handle('NEMA.scad')
coupling = _handle('coupling.scad')

zlink = _handle('ZLink.scad')
bar_clamp = _handle('bar-clamp.scad')
belt_clamp = _handle('belt-clamp.scad')
cable_clips = _handle('cable_clips.scad')

heated_bed = _handle('heated_bed.scad')
rambo = _handle('RAMBo.scad')
power_supply = _handle('PowerSupply.scad')
endstop = _handle('endstop.scad')

extruder = _handle('lasercut_extruder.scad')
small_gear = _handle('small_extruder_gear.scad')
large_gear = _handle('large_extruder_gear.scad')

spool_holder = _handle('FilamentSpoolHolder.scad')


def call(module_name, **kwargs):
    """Call an OpenSCAD module whose name is not a Python identifier.

    ``608zz_bearing`` starts with a digit, so ``import_scad`` cannot
    expose it as an attribute.  The ``use`` header for its file is
    emitted by the import above all the same, so naming the module
    directly is enough.
    """
    return OpenSCADObject(module_name, kwargs)


def scad_sources():
    """Every OpenSCAD source and header the design is built from.

    Deliberately the whole directory rather than a per-node closure:
    OpenSCAD's own ``include``/``use`` graph is not visible to the
    framework's Python import walk, and an over-approximation costs an
    unnecessary rebuild where a missing file would serve stale geometry.
    """
    return {
        os.path.join(SOURCE_DIR, entry)
        for entry in os.listdir(SOURCE_DIR)
        if entry.endswith(('.scad', '.h'))
    }
