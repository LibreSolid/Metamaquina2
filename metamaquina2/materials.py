"""Part colours, taken from the design's own material palette.

``render.h`` colours each solid by the stuff it is made of, through its
``material()`` module.  The node tree cannot use that module -- a
node's colour is a property of the node, not of the geometry it
renders -- so the same palette is restated here as the hex colours the
viewer wants.  A part's node carries the colour of the material it is
made from, exactly as the OpenSCAD source declares it.
"""

# lasercut plywood or MDF sheet
SHEET = '#fcd3a7'

# raw and threaded steel
METAL = '#b3b3b3'
THREADED_METAL = '#999999'

# printed plastic
PLA = '#f25959'
ABS = '#595959'

# the heated bed and the electronics
PCB = '#ff0000'
GLASS = '#9999ff'
ACRYLIC = '#ff9999'

# everything else the palette names
RUBBER = '#1a1a1a'
NYLON = '#ffffcc'
PEEK = '#f5f5dc'
GOLD = '#ffd700'

# Two the palette does not name, because the design draws neither part:
# the hot end's PTFE liner and the ceramic body of its heater resistor.
# The first is the palette's own `silk`, which is white, under the name
# of the stuff it is; the second has no entry to borrow and is the pale
# grey-beige a cemented wirewound resistor is potted in.
PTFE = '#ffffff'
CERAMIC = '#e8e0d0'
