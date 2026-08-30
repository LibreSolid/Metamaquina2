"""M8 hex nut."""

from build123d import RegularPolygon, extrude
from solid_node.node import Build123dNode

from metamaquina2 import materials, thread
from metamaquina2.params import m8_diameter, m8_nut_R, m8_nut_height


class M8Nut(Build123dNode):
    """A plain M8 hex nut, sitting on the XY plane.

    The design draws this as a hexagon with an 8 mm hole through it,
    which is a nut everywhere a nut is only a thing that holds a bolt
    down.  Two of them are not: the pair in the Z links carry the X
    stage, and a hole is not something a bar can hold.  So the hole is
    the thread, cut by `thread` grown by its own clearance -- the same
    profile the bar is drawn from, which is what makes the pair fit
    rather than merely both be called M8.

    The hexagon is the design's own, across flats, and the thread is
    phased from the nut's base, so a nut says nothing about where on a
    bar it sits.  The assembly says that, by turning the bar.
    """

    color = materials.METAL

    def render(self):
        blank = extrude(
            RegularPolygon(radius=m8_nut_R * 2 / 3 ** 0.5, side_count=6),
            amount=m8_nut_height)
        return blank - thread.thread(
            m8_nut_height + 2 * thread.PITCH, base=-thread.PITCH,
            diameter=m8_diameter, clearance=thread.CLEARANCE)
