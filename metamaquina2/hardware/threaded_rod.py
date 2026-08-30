"""A length of M8 threaded bar."""

from solid_node.node import Build123dNode

from metamaquina2 import materials, thread
from metamaquina2.params import m8_diameter


class ThreadedRod(Build123dNode):
    """One threaded bar, standing on the origin and running up +Z.

    The design draws these inline, as a cylinder at the major diameter,
    and says so: the thread is not modelled.  For the four bars that
    only stiffen the frame nothing turns on that.  For the two of the Z
    axis it is the whole mechanism -- a nut cannot hang on a cylinder,
    and a cylinder that turns lifts nothing -- so the thread is drawn
    here, from `thread`, and the frame's bars get it too because they
    are the same bar.

    Exact rather than tessellated, which is why this is the one bought
    part in the tree that leaves OpenSCAD behind: a helix has a closed
    form, a boundary kernel keeps it, and a nut's clearance on it is
    then a fact about the thread rather than about how finely two
    meshes were cut.
    """

    color = materials.THREADED_METAL

    def __init__(self, length, diameter=m8_diameter, **kwargs):
        self.length = length
        self.diameter = diameter
        super().__init__(length, diameter, **kwargs)

    def render(self):
        return thread.thread(self.length, diameter=self.diameter)
