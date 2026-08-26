"""The X axis belt."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.params import (
    IdlerRadius,
    PulleyRadius,
    XEnd_box_size,
    XIdler_height,
    XMotor_height,
    belt_width,
    machine_x_dim,
    thickness,
)
from metamaquina2.scad import machine


class XBelt(ScadPart):
    """One closed loop of GT2 belt around the motor pulley at one end
    and the idler bearing at the other.

    Drawn in its own vertical plane: +x runs along the beam and +y is
    up.  The two wrap radii differ because a toothed pulley and a
    608 idler are not the same size.
    """

    color = materials.RUBBER

    def render(self):
        pulley_x = -machine_x_dim / 2 + thickness + XEnd_box_size / 2
        idler_x = machine_x_dim / 2 - thickness - XEnd_box_size / 2
        return machine.belt(
            bearings=[
                [pulley_x, XMotor_height, PulleyRadius],
                [idler_x, XIdler_height, IdlerRadius],
            ],
            belt_width=belt_width,
        )
