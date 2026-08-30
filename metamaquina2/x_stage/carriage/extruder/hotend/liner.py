"""The PTFE liner the filament runs down."""

from metamaquina2 import jhead, materials
from metamaquina2.params import (
    PTFE_liner_bore,
    PTFE_liner_diameter,
    PTFE_liner_mouth,
    PTFE_liner_mouth_depth,
    PTFE_liner_tip,
    epsilon,
)
from metamaquina2.part import ScadPart, curve


class PTFELiner(ScadPart):
    """The tube inside the holder, hanging from its own top face.

    The design draws this part -- `PTFE_liner.scad` -- and what it draws
    is a shop drawing rather than a part: a 2D outline with the
    dimension arrows on it, and a 3D module that revolves the outline
    with the arrows still there.  Nothing in the design calls either.
    So the outline's own numbers are restated in `params` with the
    module they come from, and the tube is turned from them here: the
    same four boundaries the outline has -- the barrel, the point, the
    bore and the mouth -- as four bodies rather than as a hull with two
    holes taken out of it.

    Every one of them survives except the length.  The design's outline
    is 47 mm long and the hot end has 40.3 mm of bore to offer it, and
    the two cannot be reconciled by screwing the nozzle in further --
    the stub tops out where it tops out, because the block bottoms on
    the holder's shoulder.  So this is drawn to the room its neighbours
    leave, the way a spring is, and `jhead.LINER_SHORTFALL` is what is
    missing.  Above the holder is the extruder's own 3.2 mm filament
    channel and below the stub is a 3.5 mm melt chamber; a 6.33 mm tube
    enters neither, so there is nowhere else for the other six
    millimetres to be.

    The point on the end is a drill's, 118 degrees, cut to sit in the
    cone a drill leaves.  There is no cone under it here: it comes down
    on the rim of the melt chamber and only its last tenth of a
    millimetre goes in, which is where `jhead.LINER_SEAT` comes from.
    """

    color = materials.PTFE

    def tube(self):
        """The outside: a length of PTFE with a drill point on it.

        The design draws the same two shapes as the hull of two squares
        of different widths, which is a cone from the tube's diameter
        down to its tip over the point's own length.
        """
        length = jhead.liner_length
        barrel = curve(
            'cylinder', r=PTFE_liner_diameter / 2, h=length,
        ).translate([0, 0, -length])

        point = curve(
            'cylinder', r1=PTFE_liner_tip / 2, r2=PTFE_liner_diameter / 2,
            h=jhead.LINER_POINT,
        ).translate([0, 0, -length - jhead.LINER_POINT])

        return barrel + point

    def channel(self):
        """The inside: the bore, and the mouth that funnels into it."""
        depth = jhead.liner_length + jhead.LINER_POINT
        bore = curve(
            'cylinder', r=PTFE_liner_bore / 2, h=depth + 2 * epsilon,
        ).translate([0, 0, -depth - epsilon])

        mouth = curve(
            'cylinder', r1=PTFE_liner_bore / 2, r2=PTFE_liner_mouth / 2,
            h=PTFE_liner_mouth_depth,
        ).translate([0, 0, -PTFE_liner_mouth_depth])

        return bore + mouth

    def render(self):
        return self.tube() - self.channel()
