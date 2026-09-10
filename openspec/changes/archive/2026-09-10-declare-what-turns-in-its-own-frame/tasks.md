# Tasks

Behaviour-preserving throughout: the acceptance is that every leaf's
world matrix is unchanged at every pose, so evidence is captured before
the first edit and compared after the last. Run everything from the
project root with `PYTHONPATH=.` and the workspace venv
(`/home/asa/devel/libresolid-studio/.venv`). Never run two suites at
once, and never run one while another project is building. Never edit a
test.

## 0. The working state

- [x] 0.1 Confirmed clean: `git status` reported nothing to commit on
      `main`, ahead of `origin/main` by 3 commits (`f462ba9`, `fc2c8cd`,
      `dbaadce`). `git rev-parse --show-toplevel` confirmed this
      project's own root before any edit.
- [x] 0.2 Confirmed the framework version this change is written
      against: `PYTHONPATH=. .venv/bin/python -c "import solid_node;
      print(solid_node.__file__)"` from the workspace root printed
      `solid-node/solid_node/__init__.py` (the primary checkout, `main`
      at `91c0b2a`, which carries both ADR-096 `repeat-fan-out` and
      ADR-097 `joint-frame-follows-declarer`).

## 1. Baseline (broken on main before this change)

- [x] 1.1 **Baseline: 58/67 passed, 9 failed** (faceted kernel, volume
      epsilon 0 mm³), 136–155 s. Every failure was on the X or Y
      pulley — `test_each_motor_pulley_is_the_one_the_bill_of_materials_buys`,
      `test_each_motor_pulley_straddles_the_belt_it_drives`,
      `test_the_x_end_is_dimensioned_for_the_pulley_it_buys`,
      `test_the_x_pulley_meshes_with_its_belt`,
      `test_the_x_pulley_turns_one_groove_per_belt_tooth`,
      `test_the_y_belt_turns_its_teeth_onto_the_pulley`,
      `test_the_y_pulley_meshes_with_its_belt`,
      `test_the_y_pulley_sits_on_its_motor_shaft`,
      `test_the_y_pulley_turns_one_groove_per_belt_tooth` — exactly the
      two `Revolute`s whose `at` restates the parent's placement under
      the OLD reading and now applies it twice under ADR-097. Full log:
      `/tmp/claude-1000/-home-asa-devel-libresolid-studio/51062ef7-4e6c-4bbf-8b75-db00d7533d96/scratchpad/mm2_baseline.log`.
- [x] 1.2 BEFORE poses reused from the framework campaign's own
      pre-change capture (run against the confirmed-original,
      pre-ADR-097 `solid_node/motion/joints.py`, not this package's
      broken-on-main state):
      `<scratchpad>/before2/Metamaquina2-Metamaquina2-before.json`, 11
      poses / 452 leaves.

## 2. Own-frame restatement (ADR-097)

- [x] 2.1 `YPulley.spin` (`metamaquina2/y_axis/motor/y_motor.py`):

          spin = Revolute(axis=(-1, 0, 0), at=(0.0, SHAFT[0], SHAFT[1]),
                          unit='deg')
      becomes

          spin = Revolute(axis=(0, 0, 1), unit='deg')

      Axis and anchor both carried by hand and verified against the
      pre-change framework's own `Joint._carry()` output (see the
      framework campaign's `notes_Metamaquina2.md`): axis
      `(-1,0,0)` in the parent frame carries to `(0,0,1)` locally
      through `render()`'s `rotate(90,[1,0,0]).rotate(-90,[0,0,1])`;
      the anchor's only nonzero component (3.0, `SHAFT[1]`) lies along
      the new axis and is inert (`T(anchor) @ R(θ,axis) @ T(-anchor) ==
      R(θ,axis)` for any anchor parallel to axis), so it is dropped
      rather than renumbered. Docstring rewritten to state the carry in
      words instead of narrating the now-deleted anchor.
- [x] 2.2 `XPulley.spin` (`metamaquina2/x_stage/ends/motor/belt_side.py`):

          spin = Revolute(axis=(0, 0, 1),
                          at=(XEnd_box_size / 2, XMotor_height, 0.0),
                          unit='deg')
      becomes

          spin = Revolute(axis=(0, 0, 1), unit='deg')

      Axis unchanged (the parent places this body by a pure
      translation, so no rotation is inverted); anchor dropped (its X
      and Y exactly restated the parent's own translate, its Z lay
      along the axis — inert either way). Docstring rewritten the same
      way.
- [x] 2.3 Confirmed no change needed at the three remaining
      `Revolute`/`Prismatic` sites: `YPlatform.slide`
      (`y_axis/platform/y_platform.py:85`) and `XCarriage.travel`
      (`x_stage/carriage/x_carriage.py:94`) sit on bodies with an
      identity rest placement (`YAxis.render()` /
      `XStage.render()` never translate or rotate them); `XStage.lift`
      (`x_stage/x_stage.py:77`) is moved by a pure translation
      (`STAGE_REST`) and is a `Prismatic`, whose `at` never affects
      placement regardless of frame.

## 3. Hand-turned to declared (ADR-096 + ADR-097)

- [x] 3.1 `metamaquina2/hardware/threaded_rod.py`: added
      `SpinningThreadedRod(ThreadedRod)` declaring
      `spin = Revolute(axis=(0, 0, 1), unit='deg')`, no `at`. Plain
      `ThreadedRod` (used unturned by `frame/bars/front_bars.py` and
      `frame/bars/rear_bars.py`) is untouched — this resolves the
      framework survey's own OPEN QUESTION in favour of a dedicated
      subclass, so the frame's four static bars never carry an unused
      joint.
- [x] 3.2 `metamaquina2/hardware/shaft_coupling.py`: added
      `spin = Revolute(axis=(0, 0, 1), unit='deg')` directly on
      `ShaftCoupling` — it has no other consumer, so there is no
      OPEN QUESTION here.
- [x] 3.3 `metamaquina2/z_axis/z_bars.py`: `bars = ThreadedRod(...)`
      becomes `bars = SpinningThreadedRod(...)`. Added the class-body
      relation `angle.drives(bars.spin)`, fanning out over both
      `.repeat(2)` copies. Deleted:

          def simulate(self):
              for bar in self.bars:
                  bar.rotate(self.angle.value, [0, 0, 1])

      `render()` is unchanged. Docstring rewritten: the paragraph that
      described `simulate()` turning the bars now describes the
      declared `spin` joint and the one relation driving both copies.
- [x] 3.4 `metamaquina2/z_axis/z_couplings.py`: same shape. Added
      `angle.drives(couplings.spin)`; deleted
      `simulate()`'s hand `.rotate()` loop; docstring rewritten the
      same way.
- [x] 3.5 Sanity check before running the suite:
      `PYTHONPATH=. .venv/bin/python -c "from metamaquina2.metamaquina2
      import Metamaquina2; Metamaquina2()"` constructs without error.

## 4. Evidence

- [x] 4.1 **After: 67/67 passed, 0 failed** (faceted kernel, volume
      epsilon 0 mm³), 257.08 s — all nine baseline failures fixed, no
      new red. Full log:
      `/tmp/claude-1000/-home-asa-devel-libresolid-studio/51062ef7-4e6c-4bbf-8b75-db00d7533d96/scratchpad/mm2_after_suite.log`.
- [x] 4.2 Captured AFTER poses on `main` (post-edit):
      `PYTHONPATH=. .venv/bin/python
      docs/motion-general-refactor/capture_poses.py capture
      metamaquina2.metamaquina2:Metamaquina2 <scratchpad>/Metamaquina2-Metamaquina2-after.json`
      — 11 poses, 452 leaves.
- [x] 4.3 **Compared: max deviation 0.000e+00 over 11 poses.** No
      nonzero entry to explain. `compare` output:
      `max deviation 0.000e+00 over 11 poses`.

## 5. Deviations from the survey's prediction

- [x] 5.1 None. Every literal the survey and the patch script predicted
      matched exactly; the structural addition (§3) follows the
      survey's own sketch in `notes_Metamaquina2.md`, resolving its one
      open question (subclass vs. base class for `ThreadedRod.spin`) in
      favour of the subclass, as reasoned in proposal.md and task 3.1.
