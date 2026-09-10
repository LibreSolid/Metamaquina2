# Declare what turns in its own frame

## Why

solid-node main (91c0b2a) shipped ADR-097,
`joint-frame-follows-declarer`: a class-body joint's `axis`, `at` and
`carries` are now read in the declaring body's OWN rest frame, not the
parent's, and `at` defaults to the body's own origin. This is the rule
the framework's own survey (archived
`solid-node/openspec/changes/archive/2026-09-10-joint-frame-follows-declarer/`)
found this package needed: two `Revolute`s here state their `at` and,
for one of them, their `axis`, in the OLD parent-frame reading. On the
new framework those two are silently wrong wherever the anchor is not
along the axis — an `at` now applies the same offset twice — which is
why this package built the two pulleys' pose incorrectly on main before
this change (58/67 tests red, all nine on the X and Y pulleys).

Main also shipped ADR-096, `repeat-fan-out` (d07b14c): a relation
declared once in a parent's class body can drive every copy of a
`.repeat()` child, the copy carrying its own `index`. That is the
second half of what this package's own Z bars and couplings were
missing (recorded when they were first moved onto the motion layer,
2026-09-09, archived `2026-09-09-move-onto-motion`): both are turned by
a hand-written `.rotate()` in `simulate()` because a `Revolute` at each
copy's own origin used to mean the PARENT's origin — wrong for two
bars/couplings standing away from it along X — and a `.repeat()` child
could not be driven by one relation anyway. ADR-097 removes the first
blocker (a joint's default anchor is now the copy's OWN placed origin);
ADR-096 removes the second (one relation can now drive both copies).
Together they let the bars and couplings become declared joints with no
hand-written rotation left in `simulate()`.

## What changes

**Own-frame restatement (ADR-097), two sites:**

- `YPulley.spin` (`metamaquina2/y_axis/motor/y_motor.py`): axis carried
  from the parent-frame `(-1, 0, 0)` to the own-frame `(0, 0, 1)`;
  anchor `at=(0.0, SHAFT[0], SHAFT[1])` dropped (its only nonzero
  component lay along the new axis, hence inert under either reading).
- `XPulley.spin` (`metamaquina2/x_stage/ends/motor/belt_side.py`): axis
  unchanged, `(0, 0, 1)`, because the parent places this body by a pure
  translation; anchor `at=(XEnd_box_size / 2, XMotor_height, 0.0)`
  dropped (its across-axis components exactly restated the parent's own
  translation, its along-axis component inert).

Both rewrites are exact literal substitutions, verified against the
pre-change framework's own `Joint._carry()` output for the current
declared values (see `patch_Metamaquina2.py` /
`notes_Metamaquina2.md` in the framework campaign's evidence, reproduced
in `tasks.md` below). Three further joints in this package —
`YPlatform.slide`, `XCarriage.travel`, `XStage.lift` — need no change:
the first two sit on bodies with an identity rest placement, the third
is a `Prismatic` moved by a pure translation, so its `at` (already
undeclared) is inert either way.

**Hand-turned to declared (ADR-096 + ADR-097), two sites:**

- `ThreadedRod` gains a subclass, `SpinningThreadedRod`, declaring
  `spin = Revolute(axis=(0, 0, 1), unit='deg')`. Only `ZBars` uses the
  subclass; the frame's four static stiffening bars
  (`frame/bars/front_bars.py`, `frame/bars/rear_bars.py`) keep plain
  `ThreadedRod`, so they never carry an unused joint.
- `ShaftCoupling` gains `spin = Revolute(axis=(0, 0, 1), unit='deg')`
  directly on the base class: it has no other consumer.
- `ZBars.simulate()` and `ZCouplings.simulate()` are deleted. Each
  class instead declares one class-body relation fanning out over its
  `.repeat(2)` children: `angle.drives(bars.spin)` and
  `angle.drives(couplings.spin)`. `render()` is unchanged in both — it
  still stands the two copies where they belong; only the turn moves
  from a hand `.rotate()` call to the declared joint.

Both rods and both couplings turn about their own placed `+Z`
regardless of which side `render()` translates them to (`ThreadedRod`'s
own docstring: "standing on the origin and running up +Z"; the
`ShaftCoupling` OpenSCAD source is a `cylinder(...)` at the origin), so
no anchor is needed on either declaration — exactly the case ADR-097
exists to let a project state.

No pose moves: `Metamaquina2.z.drives(z_axis.bars.angle, ...)` and
`.drives(z_axis.couplings.angle, ...)` (the external wiring in
`metamaquina2/metamaquina2.py:359-360`) are untouched, and every
internal wiring change here reproduces exactly what the deleted
`simulate()` methods did by hand.

## Impact

- Affected files: `metamaquina2/y_axis/motor/y_motor.py`,
  `metamaquina2/x_stage/ends/motor/belt_side.py`,
  `metamaquina2/hardware/threaded_rod.py`,
  `metamaquina2/hardware/shaft_coupling.py`,
  `metamaquina2/z_axis/z_bars.py`, `metamaquina2/z_axis/z_couplings.py`.
- No test is edited. No spec delta: `openspec/specs/machine-motion/spec.md`
  describes driver behaviour, and every pose is proven unchanged
  (§ tasks.md, 0.000e+00 max deviation over 11 poses / 452 leaves).
- Not archived by this change: the orchestrating session reviews stage
  B before archival, per the campaign's own discipline
  (`docs/motion-general-refactor.md` in the libresolid-studio shop).
