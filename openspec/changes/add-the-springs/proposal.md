## Why

The design buys compression springs in three places and draws none of them.
Two of those three are adjustments a maker makes with their hands:

- Four CM351 springs (D=4.5 mm, free 15.3 mm) hold the heated bed up off the
  Y platform at its four corners. An M3x30 through each corner and a nut
  under the platform pull the bed down against its spring, which is how the
  bed is levelled. `heated_bed.scad:83-88` buys the four springs, the four
  bolts, twelve M3 washers and four wing nuts inside a block headed
  `//TODO: Add these parts to the CAD model`.
- Two CM1678 springs (D=6 mm, free 16.5 mm) ride the extruder handle's two
  M4x70 bolts and press the idler arm onto the filament, so the hobbed bolt
  can drag it into the hot end. `lasercut_extruder.scad:465-470` buys them
  under the same `//TODO`.

A spring is precisely the part solid-node's flexible leaf exists for: its
*shape*, not just its placement, is a function of assembly state — how far
the bed has been levelled down, how hard the idler is preloaded. The belts
already proved molejo on this machine; a helix is the other half of the
vocabulary and the thing molejo was named for.

Drawing the bed spring also settles a place where the design writes the same
height down twice and disagrees with itself. `Metamaquina2.scad:169-170`
derives `pcb_height` as the platform deck plus the sheet plus
`heatedbed_spring_compressed_length` (7.4 mm), taking the deck from
`YPlatform_height` (84.7). But `YPlatform_subassembly` stands that same deck
at a literal `100-15` (`Metamaquina2.scad:2209`, marked `/*TODO*/`) — 0.3 mm
higher. So the gap the two placed parts actually leave is 7.1 mm, not the
7.4 mm the spring variable names. A spring drawn to 7.4 would not touch the
platform it stands on. A spring drawn to the gap does.

The third pair of springs — two CM1516 for the Z-links, one at each X end —
is deliberately out of scope: they are part of the Z-link's backlash take-up,
not of these two adjustments, and the Z-link has open questions of its own.

## What Changes

- A compression spring becomes a leaf kind this project knows: a molejo
  helix swept from a round wire section, with one port carrying the length
  it is installed at. `metamaquina2/spring.py` holds what a compression
  spring *is* here, the way `gt2.py` holds what a belt is.
- The wire diameter and the coil count are **derived, not written down**.
  The bill of materials names only an outside diameter and a free length, so
  the wire is the thickness that leaves a declared clearance between the
  coil's bore and the shank it is threaded on, and the coil count is the
  most turns that still leave a clear wire diameter between consecutive
  coils at the length the design installs the spring at. Both come out at
  round numbers for both springs.
- The Y platform gains four bed levelling screws, each a small assembly: an
  M3x30 down through the heated bed and the platform, three M3 washers, the
  spring between the two sheets, and a nut under the platform. The spring's
  installed length is derived from the placements the wrapper already makes
  — the platform deck's top face and the underside of the bed board — so it
  fills the gap rather than restating either of the design's two numbers for
  it.
- The extruder handle gains the two idler springs and the two M4 washers the
  bill of materials buys for them, seated on the outer face of the idler's
  back plate, drawn at their free length because the design states no
  preload: it leaves 7.75 mm of bare shank between the spring and the bolt
  head, which is the adjustment its (undrawn) lock nut is for.
- The handle's placement moves out of `extruder.py` into a named constant in
  `handle.py`, so the handle can derive where the idler's back plate stands
  in its own frame instead of a second copy of the offset being written down.
- `idler.py` publishes where its back plate's outer face stands, for the same
  reason.
- `params.py` probes `heatedbed_spring_length`,
  `heatedbed_spring_compressed_length`, `m4_diameter`, `m4_washer_thickness`
  and `m3_washer_D`, and restates the heated bed's mounting-hole inset, which
  the design writes inside a module body.

Not in this change, and deliberately:

- **No new driver.** Both ports are bound to the length the design's own
  geometry gives. Levelling the bed as a driver would move
  `BuildPlatform_height`, which is where Z is measured from; opening the
  idler as a driver would swing the arm the design draws closed. Both are
  real machine states and both are a change to `machine-motion`, which is the
  pilot's call, not this change's. The ports exist so that call costs a
  `connect()`.
- **No wing nut and no M4 lock nut.** The bill of materials buys a "Borboleta
  M3" at the bed and M4 lock nuts at the handle; the design draws neither,
  and neither has a catalogue dimension anywhere in the sources. The bed gets
  the plain M3 hex nut the design does draw, recorded as a departure, and the
  handle's lock nuts stay unmodelled.
- **No closed or ground end coils.** A real compression spring's end coils
  are pitched flat and ground square. molejo sweeps one continuous helix, so
  the drawn spring has open ends, and the length it occupies is its helix
  plus one wire diameter.

## Capabilities

### New Capabilities

- `spring-loading`: the parts this machine holds against something with a
  spring — the levelled bed and the filament idler — as flexible leaves whose
  length is the space the parts around them leave, with the wire and the
  coil count derived from the catalogue line rather than invented.

## Impact

- `metamaquina2/spring.py` — new: the compression spring as a molejo leaf.
- `metamaquina2/y_axis/platform/bed_spring.py`,
  `metamaquina2/y_axis/platform/level_screw.py` — new.
- `metamaquina2/y_axis/platform/y_platform.py` — four levelling screws at the
  bed's own corner holes.
- `metamaquina2/x_stage/carriage/extruder/idler_spring.py` — new.
- `metamaquina2/x_stage/carriage/extruder/handle.py` — springs, washers, the
  named placement, the port wiring.
- `metamaquina2/x_stage/carriage/extruder/extruder.py` — reads that placement.
- `metamaquina2/x_stage/carriage/extruder/idler/idler.py` — publishes the back
  plate's outer face.
- `metamaquina2/params.py` — five more probed names, one more module-body
  value.
- `metamaquina2/metamaquina2.py` — the module docstring, which is this
  package's own account of what it reads.
- `metamaquina2/test_metamaquina2.py` — the contracts below.
