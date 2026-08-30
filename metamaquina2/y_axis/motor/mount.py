"""Where the Y motor's shaft stands.

Its own module because two things need it and neither can own it. The
belt needs it because the loop is drawn around the pulley on that shaft,
and the motor needs it because the pulley has to be put there -- and the
belt cannot import the motor, which needs the belt's pitch to cut its
pulley at.

The numbers are the design's. `YMotorAssembly` bolts the motor into its
holder with ``translate([40,-60,-7])`` and `RearAssembly` then stands the
whole holder on end behind the upper rear bar, and between them those
place a shaft the design never had to locate precisely: its own
`GT2_pulley` draws nothing, so nothing was ever measured against it.
"""

from metamaquina2.params import (
    RightPanel_basewidth,
    bar_cut_length,
    feetheight,
)


#: The design's own offset of the motor within the holder assembly, from
#: ``translate([40,-60,-7])``. The first two numbers place the shaft in
#: the holder's face and the third is along it.
ACROSS = 40
ALONG = 60
DEPTH = 7

#: Where the holder plate meets the rear bars.
HEIGHT = 60 + feetheight + 12

#: The shaft's axis in the machine, as ``(y, z)``.
#:
#: The mount stands the holder assembly on end -- a quarter turn about
#: the machine's Y and a half turn about its Z -- which lands the
#: holder frame's `ACROSS` on the machine's Z, downwards from `HEIGHT`,
#: and its `ALONG` on the machine's Y, forwards from the rear bar. The
#: shaft itself then runs along the machine's X, which is the axis both
#: belts run their width along.
SHAFT = (RightPanel_basewidth / 2 - bar_cut_length - ALONG, HEIGHT - ACROSS)
