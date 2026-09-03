"""The two vertical threaded bars that lift the X stage."""

from solid_node.node import AssemblyNode, RotationalPort

from metamaquina2.hardware.threaded_rod import ThreadedRod
from metamaquina2.params import (
    XZStage_offset,
    Z_bar_length,
    lm8uu_diameter,
    machine_x_dim,
    thickness,
    z_rod_z_bar_distance,
)
from metamaquina2.z_screw import BAR_BASE


class ZBars(AssemblyNode):
    """Two M8 threaded bars, each driven by its own motor below it.

    They start at the top of the motor shaft, where the coupling joins
    them, and run to the top of the machine.

    Both turn, and `angle` is how far.  It comes in from outside
    because a bar has no opinion about it: what turns these is a pair
    of motors taking a Z command, and the height that command means is
    the machine's arithmetic and not the bar's.  So this assembly no
    longer builds on its own -- an unconnected port has no value, and
    asking for one says so instead of quietly drawing a screw that
    stands still under a stage it is supposed to be holding up.

    Both bars take the same angle.  The motors face each other, which
    is a fact about how they are bolted under the panel and not about
    which way they turn: two nuts rising together are two screws
    turning the same way, and a machine whose bars disagreed would rack
    its own beam.

    Where a bar stands never changes -- it is held between the motor
    below it and the top of the machine -- so `render` stands the two
    of them once, and the turn is all that is left to `simulate`.  A
    turn applied there goes on before the placement, which is what a
    bar spinning about its own axis rather than swinging around the
    middle of the machine needs, and it is stated absolutely for its
    instant, so a new height replaces it rather than piling onto it.
    """

    angle = RotationalPort(unit='deg')

    #: How far out from the middle of the machine each bar stands.
    offset = (machine_x_dim / 2 - thickness - lm8uu_diameter / 2
              - z_rod_z_bar_distance)

    bars = ThreadedRod(length=Z_bar_length).repeat(2)

    def render(self):
        for side, bar in zip((-1, 1), self.bars):
            bar.translate([side * self.offset, -XZStage_offset, BAR_BASE])

    def simulate(self):
        for bar in self.bars:
            bar.rotate(self.angle.value, [0, 0, 1])
