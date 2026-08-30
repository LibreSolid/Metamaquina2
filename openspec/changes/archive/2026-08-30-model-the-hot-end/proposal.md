## Why

The machine has no hot end. `XCarriage` says so in its own docstring and
gives the reason: `jhead.scad` still carries the conflict markers of a merge
that was never finished, so OpenSCAD refuses to parse the file, drops
`J_head_assembly` with `WARNING: Ignoring unknown module`, and the design's
own whole-machine rendering has been coming out with nothing under the
carriage for as long as that has been true.

That is not a cosmetic gap. The hot end is where the machine is measured
from. `Metamaquina2.scad:222` derives

    nozzle_tip_distance = jhead_length - jhead_instalation_depth
                          - thickness - XCarriage_height

and `Metamaquina2.scad:2809` lifts the whole X platform by it, so that the
nozzle tip stands exactly `ZCarPosition` above the build surface and `HomeZ`
brings it down onto the glass. Every Z contract in this repository is
written against a point no part reaches, because the part that would reach
it is not drawn. `test_homing_z_winds_the_beam_down_to_the_build_surface`
says in its own docstring that "the nozzle really has to arrive at the build
surface" and then has to settle for asking the beam, because there is no
nozzle to ask.

The parts are bought and the drawings are in the repository. The bill of
materials buys five of them — `JHead machined body` (MM2_PEEK), `PTFE liner`
(MM2_PTFE_liner), `J-Head 0.35mm nozzle` (035_NZ), `extruder thermistor`
(TV100000X) and `extruder heater resistance` (UB5C-5RF1) — three of those
under blocks headed `//TODO: Add this part to the CAD model`, and
`lasercut_extruder.scad:552` buys the two `M3x30` that hold the assembly in
the extruder block. `doc/Jhn_nozzle_holder_v4.jpg` is the dimensioned shop
drawing of the PEEK holder and `doc/Jhn_md_brass_heater_nozzle.jpg` is the
dimensioned shop drawing of the brass nozzle. Nothing here is invented; it
is drawn and bought and never modelled.

## What Changes

- The machine gains a hot end: a `HotEnd` assembly hanging in the extruder
  where the design hangs `J_head_assembly()`, holding the PEEK nozzle
  holder, the PTFE liner inside it, the brass nozzle screwed into its foot,
  and the heater resistor and thermistor in the holes the nozzle is drilled
  for. The extruder gains the two M3x30 the design cuts holes for.
- `metamaquina2/jhead.py` holds what a J-head is here, the way `gt2.py`
  holds what a belt is: the two shop drawings' own numbers, and the stack
  arithmetic that turns them into where each part stands.
- **The holder's length is derived, not written down.** Its drawing is the
  one place in this hot end that declares a dimension free — "36.5mm or 50mm
  (length not critical)" — and the machine is not free about it at all:
  `jhead_length` and `jhead_instalation_depth` are what the whole X platform
  is lifted by. So the length of the 5/8" PEEK body is what leaves the
  nozzle tip exactly `jhead_length - jhead_instalation_depth` below the face
  the extruder clamps, and it comes out at 42.277 mm of body, 52.947 mm of
  holder. Every other dimension of both parts is the drawing's.
- **The filament bore is derived too**, from two numbers the design already
  states and one the drawing does. The holder's grooves are cut to a root of
  ⌀10.4 — the core `jhead.scad` draws its own body around — and the drawing
  leaves a wall of 0.078" to 0.094" at a groove. Only the thin end of that
  range leaves a bore the design's own PTFE liner passes down: ⌀6.4376 over
  a ⌀6.33 liner, 0.054 mm of clearance all round, which is the press fit a
  PTFE liner is really fitted with. The fat end of the range would give
  ⌀5.62 and no liner at all.
- **The liner is drawn to the room the holder and the nozzle leave it.**
  `PTFE_liner.scad` draws a 47 mm liner; between the holder's top face and
  the top of the nozzle's threaded stub there are 40.247 mm. The two cannot
  both be true — the design's own overall length leaves 40.247 mm of bore
  whatever the nozzle is screwed in to — so the placements win and the
  disagreement is recorded where the length is derived, exactly as the bed
  spring's is. The liner keeps every other number the design draws it with:
  ⌀6.33 outside, ⌀3.0 bore, the ⌀4.5 mouth over the first 2 mm, and the 118°
  drill point that noses into the nozzle's melt chamber.
- The nozzle itself is the design's own `v4nozzle()` from `nozzle.scad`,
  which is the brass drawing transcribed and which parses, so it is called
  and not redrawn. `scad.py` imports the file.
- `materials.py` gains the two colours the design's palette never had to
  name, because the design draws neither part: white for the PTFE liner —
  which the palette already spells `silk` — and a ceramic for the heater
  resistor's body.
- `params.py` probes `jhead_length`, `jhead_instalation_depth` and `inch`,
  and restates the module-body values the probe cannot reach: the holder's
  ⌀10.4 groove root from `J_head_body()` in `jhead.scad`, the PTFE liner's
  outline from `PTFE_liner_2d_outline()`, and the two M3x30 hole positions
  from `extruder_slice()`.

Not in this change, and deliberately:

- **`jhead.scad` is not repaired.** The conflict is over two cut cubes that
  remove nothing from the body either way — one version cuts at ±18 mm, the
  other at ±11.5 mm, and the body's own radius is 8 — so resolving it would
  restore a module whose geometry contradicts the drawing it was sketched
  from: no neck, no collar, no tapped bores, a groove root where the drawing
  puts a bore, and a stack 1.8 mm short of the `jhead_length` the machine
  measures Z from. The wrapper reads the design; it does not finish somebody
  else's merge. The file stays as it is and the departure is recorded in
  `jhead.py`.
- **No thread form.** The holder's two tapped bores (5/16-24 at the top,
  3/8-24 at the nozzle) are drawn at their tap drills — letter I and letter
  Q — which is the material the tap leaves. `thread.py` exists and could cut
  a real helix, but nothing here is measured finer than a mesh tolerance,
  which is the test this project applies to exact solids.
- **No new driver.** Nothing about the hot end moves relative to the
  extruder.
- **The block's angle is not made a parameter.** Which way the heater block
  faces is set by how far the nozzle is screwed in, so it is genuinely free;
  the design's own choice is kept, which means the hot end is drawn square
  with the machine rather than with the extruder that carries it.
- **The five M3x35 that bolt the extruder's own slices together stay
  undrawn.** They were undrawn before this change and they are not the hot
  end's.

## Capabilities

### New Capabilities

- `hot-end`: the thing that melts the filament, drawn from the shop drawings
  the repository already carries, assembled the way it is really assembled,
  and standing where the machine's own Z zero says its tip stands.

## Impact

- `metamaquina2/jhead.py` — new: what a J-head is here, and the stack
  arithmetic.
- `metamaquina2/x_stage/carriage/extruder/hotend/` — new: `hot_end.py`,
  `nozzle_holder.py`, `liner.py`, `nozzle.py`, `heater_resistor.py`,
  `thermistor.py`.
- `metamaquina2/x_stage/carriage/extruder/extruder.py` — the hot end, and
  the two M3x30 that hold it.
- `metamaquina2/x_stage/carriage/x_carriage.py` — the docstring that
  explained why there was no hot end.
- `metamaquina2/scad.py` — `nozzle.scad`.
- `metamaquina2/params.py` — three probed names, three module-body blocks.
- `metamaquina2/materials.py` — PTFE and ceramic.
- `metamaquina2/metamaquina2.py` — the module docstring.
- `metamaquina2/test_metamaquina2.py` — the contracts below.
