"""A length of M8 threaded bar."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart, curve
from metamaquina2.params import m8_diameter


class ThreadedRod(ScadPart):
    """One threaded bar, standing on the origin and running up +Z.

    Like the smooth rods, the design draws these inline rather than as
    a module, so the cylinder is drawn here.  The thread is not
    modelled, in the design or here; the bar is its major diameter.
    """

    color = materials.THREADED_METAL

    def __init__(self, length, diameter=m8_diameter, **kwargs):
        self.length = length
        self.diameter = diameter
        super().__init__(length, diameter, **kwargs)

    def render(self):
        return curve('cylinder', r=self.diameter / 2, h=self.length)
