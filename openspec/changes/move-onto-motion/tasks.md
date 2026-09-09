# Tasks

Behaviour-preserving throughout: the acceptance is that every leaf's world
matrix is unchanged at every pose, so evidence is captured before the first
motion edit and compared after the last. Run everything from the project
root with `PYTHONPATH=.` and the workspace venv
(`/home/asa/devel/libresolid-studio/.venv`). This is the largest suite in
the catalogue — never run two suites at once, and never run one while
another project is building. Never edit a test: if one blocks, stop and
report the assertion and why.

## 0. The working state

- [x] 0.1 Confirmed: `git status` was clean on `main` (only the
      untracked `openspec/changes/move-onto-motion/` proposal itself,
      `_build/` etc. ignored). Nothing to commit at stage 0.
      `git rev-parse --show-toplevel` confirmed this project.

## 1. Stage A — imports and baseline

- [x] 1.1 Import the moved names from `solid_node.motion.ports` in the
      twelve modules that name them, changing nothing else:
      `filament.py` and `spring.py` (`MolejoNode` stays from
      `solid_node.node`, `TranslationalPort` moves);
      `x_stage/x_belt.py`, `y_axis/y_belt.py` (`TranslationalPort`);
      `x_stage/x_stage.py`, `y_axis/y_axis.py` (`AssemblyNode` stays,
      `TranslationalPort` moves);
      `z_axis/z_axis.py`, `z_axis/z_bars.py`, `z_axis/z_couplings.py`,
      `x_stage/ends/motor/x_end_motor.py`,
      `x_stage/ends/motor/belt_side.py`, `y_axis/motor/y_motor.py`
      (`AssemblyNode` stays, `RotationalPort` moves).
      `metamaquina2/test_metamaquina2.py` imports no moved name and is
      NOT touched.
- [x] 1.2 Confirmed: before 1.1 the import failed at `filament.py:105`
      with `ImportError: module 'solid_node.node' has no attribute
      'TranslationalPort'`; after 1.1,
      `PYTHONPATH=. .venv/bin/python -c "import metamaquina2.metamaquina2"`
      succeeds.
- [x] 1.3 **Baseline: 67/67 passed, 0 failed** (faceted kernel, volume
      epsilon 0 mm³), 246.36 s. Every one of the 67 tests in
      `Metamaquina2Test` passed; none pre-existing red. Full names in
      `/tmp/claude-1000/-home-asa-devel-libresolid-studio/0926d69e-f321-446e-bc64-bb17a3046e16/scratchpad/mm2-stageA.log`.
- [x] 1.4 Captured 18 poses, 452 leaves ->
      `/tmp/metamaquina2-before.json`. Extra pose file at
      `/tmp/claude-1000/-home-asa-devel-libresolid-studio/0926d69e-f321-446e-bc64-bb17a3046e16/scratchpad/mm2-extra-poses.json`
      (Rest, CenterX, PresentBed, HomeZ, top, and two mixed poses; Rest
      and top come out numerically identical to the defaults pose
      because `ZCarPosition == BuildVolume_Z == 150`, both already the
      drivers' own defaults -- included anyway as instructed).
      Original 1.4:
      `PYTHONPATH=. .venv/bin/python <shop>/docs/motion-general-refactor/capture_poses.py capture metamaquina2.metamaquina2:Metamaquina2 /tmp/metamaquina2-before.json`,
      plus an `extra` pose file in NATIVE driver units (`x`, `y` in mm;
      `z` in the screws' own DEGREES, via `z_screw.angle(height)`, which
      is what `set_state` takes) covering at least:
      `Rest = {x: XCarPosition, y: YCarPosition, z: z_screw.angle(ZCarPosition)}`,
      `CenterX = {x: 0.0}`, `PresentBed = {y: -BuildVolume_Y / 2}`,
      `HomeZ = {z: 0.0}`,
      `top = {z: z_screw.angle(BuildVolume_Z)}`,
      and two poses with all three axes off nought and off each other,
      e.g. `{x: -60, y: 40, z: z_screw.angle(120)}` and
      `{x: BuildVolume_X / 2, y: BuildVolume_Y / 2, z: z_screw.angle(30)}`.
      Record the pose count and the leaf count.
- [x] 1.5 Commit as
      `refactor(simulation): import ports from solid_node.motion`,
      with the baseline suite result and the pose/leaf counts in the
      message body. Commit the proposal directory in the same commit.

## 2. Stage B — the motion refactor

Do these in order; each step leaves the model importable, so run
`python -c "import metamaquina2.metamaquina2"` after each.

- [x] 2.1 **The three belt constants per axis.** In
      `x_stage/x_belt.py`, after `pulley_angle()`, add `PITCH_ARC`,
      `BEAM_PER_DEGREE` and `PULLEY_AT_ORIGIN` exactly as the proposal
      writes them. In `y_axis/y_belt.py`, the same with
      `BED_PER_DEGREE`. `pulley_angle()` itself keeps its body: the
      phase is that function evaluated at `CLAMP_ORIGIN`. Change no
      other number.
- [x] 2.2 **The X stage's rest stand.** Add `STAGE_REST` to
      `metamaquina2.py`, place `x_stage` from it in
      `Metamaquina2.render()`, and read `stage` off it in
      `simulate()` for the filament paragraph.
- [x] 2.3 **The three prismatics.** `XStage.lift`, `XCarriage.travel`,
      `YPlatform.slide`, with axis and unit as proposed and NO `range`.
      Import `Prismatic` from `solid_node.motion.joints`.
- [x] 2.4 **The two pulley subclasses and their wirings.** `XPulley` in
      `belt_side.py` and `YPulley` in `y_motor.py`, each three lines
      carrying one `Revolute` with the axis and anchor the proposal
      derives; then `pulley = XPulley(period=PERIOD, spin=shaft)` and
      `pulley = YPulley(period=PERIOD, spin=shaft)`. Delete
      `XEndMotorBeltSide.simulate()` and `YMotor.simulate()`. Keep both
      `shaft` ports: two contracts read them.
- [x] 2.5 **The five root relations**, in `Metamaquina2`'s class body,
      replacing the `x_stage.translate` and the three `connect`s into
      `carriage_position`, `platform_position` and `screw`. Leave the
      five filament `connect`s exactly as they are.
- [x] 2.6 **The four axis relations**, two in `XStage`'s body and two in
      `YAxis`'s body, and delete both `simulate()` methods.
- [x] 2.7 **The four forwarders.** Remove `XStage.carriage_position`,
      `YAxis.platform_position`, `ZAxis.screw` (and `ZAxis.simulate()`),
      and `XEndMotor.shaft` (and `XEndMotor.simulate()`).
- [x] 2.8 **Nothing else.** `ZBars`, `ZCouplings`, `Handle` and
      `BedLevelScrew` keep their ports and their `simulate()` loops
      (Known gaps 1). No joint for the idlers, no `e` driver, no motion
      the model does not have today.
- [x] 2.9 Correct the docstrings the change makes untrue: `XStage`,
      `YAxis` and `ZAxis` on "this assembly no longer builds on its own",
      `XEndMotorBeltSide` and `YMotor` on which frame the turn is
      applied in, `XEndMotor` on relaying the shaft, and the README's
      paragraph on what `simulate()` does. Say what is now true, in the
      package's own voice; add no new claim.

## 3. Evidence

- [x] 3.1 Re-capture poses to `/tmp/metamaquina2-after.json` with the
      same extra pose file, and run
      `capture_poses.py compare /tmp/metamaquina2-before.json /tmp/metamaquina2-after.json`.
      Expected maximum deviation 0 on every leaf except possibly the two
      motor pulleys, where a sub-ulp affine restatement may show below
      1e-13 degrees (proposal, Tests item 2). Report the number, do not
      round it away.
- [x] 3.2 Run the whole suite again,
      `PYTHONPATH=. .venv/bin/solid test --faceted metamaquina2/metamaquina2.py`,
      and record every contract's result beside its stage A result. The
      same tests green as the baseline, none newly red.
- [x] 3.3 Commit as
      `refactor(simulation): move the Metamaquina 2 onto solid-node joints and couplings`,
      with the pose comparison line and the two test results in the body.

## 4. Report

- [x] 4.1 Report to the orchestrator: the two commit hashes, the pose
      comparison line with its leaf and pose counts, the test counts
      before and after with any test whose result changed, every
      deviation from this proposal and why, and every test you believe
      needs a change with the exact assertion and the reason. Do NOT
      sync or archive the OpenSpec change; the orchestrator does that
      after review.


## Evidence recorded

- 3.1: `capture_poses.py compare` reports **max deviation 0.000e+00
  over 18 poses** (452 leaves each) -- no sub-ulp deviation on either
  motor pulley; the two relations reproduce `pulley_angle()` exactly in
  floating point.
- 3.2: **67/67 passed, 0 failed** (faceted kernel, volume epsilon
  0 mm3), 230.46s -- identical to the stage A baseline, no test's
  result changed. Full names in
  `/tmp/claude-1000/-home-asa-devel-libresolid-studio/0926d69e-f321-446e-bc64-bb17a3046e16/scratchpad/mm2-stageB-final.log`.
- Deviations from the proposal: none. Every joint, wiring, relation and
  removed port/simulate() matches the proposal's "What changes"
  section exactly; the two derived belt-constant blocks and the
  `STAGE_REST` constant are copied verbatim. `end_motor.shaft`
  (the forwarding port) is removed while `belt_side.shaft` and
  `motor.shaft` are kept, per the proposal's "Kept -- seventeen" list
  and Tests item 1 (both are read by
  `test_the_x_pulley_turns_one_groove_per_belt_tooth` and
  `test_the_y_pulley_turns_one_groove_per_belt_tooth`, unchanged).
- Tests: none needed a change, and none was touched beyond the stage A
  import fix (which touched no test file). Tests items 1, 4 and 5 in
  the proposal were decisions already resolved by "as written" review
  (keep `shaft` ports, no joint range, standalone-build docstrings
  corrected rather than a rest-default guard added) and required no
  code beyond what stage B already does.
