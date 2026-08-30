## Why

The design draws the machine loaded and the machine empty at the same time.
`FilamentSpoolHolder.scad` stands a reel on the bar — a plain ABS tube from
Ø35 to Ø160, 160 mm wide — and declares `diameter=3` on line 60, which
nothing in the file uses. Three millimetres is the stock this machine eats:
`PTFE_liner.scad` bores its liner `d4 = 3.0` and calls it "the filament runs
down this", and `extruder_slice()` cuts a 3.2 mm channel 70 mm up through the
middle slice of the extruder for it to arrive by. So the design knows the
diameter three times over and draws the strand nowhere. What stands beside
the machine is a tube of ABS, and between it and the extruder there is
nothing at all.

Filament is the other thing on this machine whose shape is a function of
where the machine is, and it is the case molejo was named for after springs
and belts. A belt's loop stands still while the rubber inside it travels; a
spring is shorter when you press on it; the free run from the reel to the
extruder is neither — it is a length of stock hanging between a stand that
does not move and a print head that moves in X and in Z, and its shape at any
instant is a function of both. Sampling it is exactly what molejo's
`filament-loom` fixture exists to refuse: two axes, and a grid over both.

Drawing it also settles what the reel is. The design's tube is not a part; it
is 160 mm of wound stock drawn as the cylinder it comes to. Once the strand
is a strand, the outermost layer of it can be what it really is, and the tube
under it is what is wound below that layer — the two together still the
design's own Ø160.

## What Changes

- Filament becomes a leaf kind this project knows: a molejo sweep of the
  3 mm section the design names, along a path that is one helix — the layer
  lying on the reel — continued by one spline — the free run to the machine.
  `metamaquina2/filament.py` holds what filament is here, the way `spring.py`
  holds what a compression spring is and `gt2.py` what a belt is.
- **The layer is derived, not chosen.** Its centre line runs half a stock
  diameter inside the reel's own outside diameter, its pitch is the stock's
  own diameter because that is how a layer lies, and its turn count is the
  most whole turns of it that fit across the reel's width. Fifty-three turns
  at 3 mm come to 159 of the reel's 160.
- **`FilamentSpool` loses its outermost layer**, because that layer is now
  drawn as the strand it is. The tube is what is wound under it, one stock
  diameter smaller on the radius, and reel plus strand still reach the
  design's Ø160 exactly.
- **The free run is pinned at two points and both arrive through ports.** The
  far end is the mouth of the design's own filament channel, bound from where
  the machine puts its own extruder rather than from a position written down a
  second time. The other is where the run gets over the machine: the stand is
  beside the frame and the extruder is inside it, so a run drawn straight from
  one to the other goes through the frame's right-hand side panel, the beam's
  own plate and the box at the beam's end. It crosses at the machine's own
  edge, two stock diameters above the highest sheet the frame carries, and
  comes down through the opening the top panel is cut with for the carriage.
  Five ports rather than six: both points are in the plane the run comes in
  on, so that plane is one number and it is the same number twice.
- Driving X or Z redraws the run between its crossing and its end; the
  crossing and the layer on the reel do not move, because neither the frame
  nor a reel goes anywhere when a print head does.
- Where the entry point is is published down the chain that decides it, as
  the handle's placement was for the idler springs: `params` restates the
  channel `extruder_slice()` cuts, `extruder.py` says where it opens in the
  extruder's own frame, `x_carriage.py` in the carriage's, `x_stage.py` in
  the beam's as a function of where the carriage is, and the machine adds its
  own lift. The crossing is the frame's own height and width, so it is
  derived from `machine_height` and `machine_x_dim` and bound by the machine.
- The filament hangs off the root beside the spool holder rather than inside
  it, because it is the one part of this model that is in two places: it lies
  on a stand that does not move and it ends on a carriage that does.
- `params.py` restates the filament channel from `extruder_slice()`'s module
  body, and the stock diameter from `FilamentSpoolHolder.scad`.

Not in this change, and deliberately:

- **No new driver.** Nothing here consumes filament. The reel is drawn full,
  as the design draws it full, and the strand's shape follows the two drivers
  the machine already has. A feed driver would be a change to
  `machine-motion` and the pilot's call; when it comes, the layer's turn
  count is where it lands.
- **The run stops at the channel's mouth**, and this is a finding rather than
  a choice. Four things stand under it, and the first of them is at the mouth
  itself: the extruder handle's plate stands on the block's top face three
  tenths of a millimetre inside the channel it is beside, so the machine's own
  parts leave 2.9 mm of clear channel for 3 mm of stock and a strand drawn on
  the channel's axis grazes the plate. Below that the hobbed bolt and the
  idler bearing are drawn closed on each other, sharing metal where the
  filament would be, because the design draws the idler shut and gives no knob
  for opening it — the same reason the idler springs got no driver. Further
  down, the drawn hot end stands on the filament axis at nought while the
  design's own extruder cuts its channel, its two M3 holes and its
  nozzle-holder slot at −0.3, so the two disagree by three tenths of a
  millimetre about where the filament goes. And below that the PTFE liner's
  bore is 3.0 and the stock is 3.0, which is a bore the size of what runs
  down it and not a fit anything can be drawn in. All four are recorded where
  the run ends and asked for by contract, so none of them can quietly go away;
  settling any of them is a change to the design or to the hot end, not to the
  filament.
- **No second layer.** A molejo helix winds about the tangent it starts on,
  so a second helix chained after one starts on the first's own pitch angle
  and does not come out coaxial — a full reel is not expressible as one
  sweep, and one layer is what a reel's surface is.

## Capabilities

### New Capabilities

- `filament-path`: the stock this machine consumes, drawn from where it lies
  wound on the reel to where the machine takes it in, as one flexible strand
  whose free run follows the print head.

## Impact

- `metamaquina2/filament.py` — new: what filament is here, and the strand as
  a molejo leaf.
- `metamaquina2/spool_holder/spool.py` — the tube is what is wound under the
  outermost layer.
- `metamaquina2/spool_holder/spool_holder.py` — publishes the height it
  stands the reel at.
- `metamaquina2/x_stage/carriage/extruder/extruder.py`,
  `metamaquina2/x_stage/carriage/x_carriage.py`,
  `metamaquina2/x_stage/x_stage.py` — publish where the filament channel
  opens, each in its own frame.
- `metamaquina2/metamaquina2.py` — the strand as a child of the machine, its
  three ports bound, and the module docstring.
- `metamaquina2/params.py` — the stock diameter, and the channel restated
  from a module body.
- `metamaquina2/test_metamaquina2.py` — the contracts below.
