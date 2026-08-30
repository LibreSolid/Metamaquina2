## Why

The free run passes through the machine, and the contract that was written to
stop it doing exactly that does not catch it.

`thread-the-filament` asked for the run to share metal with nothing "at rest
and at both ends of both travels", and that is what it asks: X to each end
with Z at rest, then Z to each end with X at rest. Five poses, none of them a
corner. The requirement it was written under is stronger — "at any position
the machine's drivers can reach" — and the run only fails at the corners. Wind
the beam down to the build surface and put the carriage on the spool's side of
the machine, and the run cuts the frame's right-hand side panel, its top
panel, and both of the rod-end plates over the right-hand Z rod. Forty-eight
cubic millimetres out of the side panel alone.

The reason is the crossing, and specifically what it was derived from. It
stands two stock diameters above the highest sheet the frame carries, on the
stated ground that "above the crossing there is nothing on this machine: the Z
travel tops out at the pose the design draws". That sentence is wrong twice
over. The Z travel does not top out at the pose the design draws — `ZCarPosition`
is the middle of it and the driver reaches `BuildVolume_Z` — and at the top of
that travel the beam lifts the extruder's own channel mouth to 415.95 and the
handle plate above it to 445.95, both far above the frame's own 369.2. The
frame is not the highest thing the run has to get over. The print head is.

Pinned that low, the run has to fall a hundred and sixty millimetres in the
hundred and seventeen the crossing leaves it, so it leaves the crossing already
dropping and reaches the side panel's own x thirty-six millimetres below the
top panel it was supposed to come down through. Raise the crossing to where
the machine actually needs it and the same two-point run clears everything,
everywhere: the constraint the bottom of the travel imposes and the constraint
the top of the travel imposes turn out to be within six millimetres of each
other.

## What Changes

- **The crossing is derived from the print head rather than from the frame.**
  It stands two stock diameters above the highest the machine's own head ever
  stands, which is the extruder handle's plate with the beam at the top of its
  declared Z travel. The rule is the one it always was — clear of the highest
  thing in the way, by two stock diameters — applied to the right thing.
- **The height the head reaches is published down the chain that decides it**,
  exactly as the entry point already is: `handle.py` says how high its plate
  stands in the extruder's frame, `extruder.py` that this is the highest the
  extruder stands, `x_carriage.py` and `x_stage.py` restate it in their own
  frames, and the machine adds the lift its own declared travel reaches. No
  height is written down a second time.
- **`CROSSING_X` and `CROSSING_Z` move from `filament.py` to
  `metamaquina2.py`.** What they are made of is now the beam and the travel,
  and both are the machine's. `filament.py` goes back to saying only what
  filament is.
- **The routing contract asks the corners.** At rest and at the four corners
  of the two travels, rather than at each axis' ends with the other at rest.
  The corners subsume the single-axis ends and cost the same five poses.
- **The finding is asked for by contract**: with the beam at the top of its
  travel the print head stands above every sheet the frame carries, so a
  crossing derived from the frame would be under the head; and the run's
  crossing stands clear above the head there. Neither can quietly go away.
- `params.py` gains `HandleHeight`, which the design declares beside
  `HandleWidth` and this is the first thing to need.

Not in this change, and deliberately:

- **The route keeps its shape.** One helix continued by one two-span spline,
  pinned at the same two places, through the same five ports. Only the height
  of one of them changes, so the strand costs exactly what it cost.
- **The run still stops at the channel's mouth**, for the four reasons
  `thread-the-filament` recorded. Nothing here touches them.

## Findings not settled here

The run also draws mirrored in the viewer, and that is not this model's fault.
`Metamaquina2` publishes the far end of the run as
`(-((((-100.0 + x) - -100.0) + 0) - 400))`, which is `400 - x` in the Python
that emitted it and in any JavaScript that reads it. The viewer's own
evaluator answers `400 + x`: `jokenizer`, the parser
`solid_node/viewers/widget/src/evaluator.ts` builds on, binds a leading unary
minus looser than the `+` beside it, so it reads `-100.0 + x` as
`-(100.0 + x)`. The end of the run therefore tracks the carriage backwards
about the middle of the travel, which is exactly what a mirrored coefficient
does.

Every one of the 265 distinct expressions this machine publishes was evaluated
both ways and compared; that one is the only disagreement, so nothing else in
the model is affected. It is a framework defect rather than a project one —
the model's own geometry is right at every position, and no contract this
project can write would catch it, because a project test evaluates the
expression in Python and Python reads it correctly. It belongs to solid-node,
and it is recorded here so the report survives this change.
