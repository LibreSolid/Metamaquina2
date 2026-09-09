# Move the Metamaquina 2 onto solid-node's motion layer

## Why

solid-node main moved `Port`, `RotationalPort`, `TranslationalPort`,
`SignalPort`, `Time`, `bind`, `connect` and `declared_ports` out of
`solid_node.node` into `solid_node.motion.ports` with no re-export, so
this package does not import:

    ImportError: module 'solid_node.node' has no attribute
    'TranslationalPort': ports and the declared time base moved to
    'solid_node.motion.ports'. Write `from solid_node.motion.ports
    import TranslationalPort`. solid_node.node answers what has shape;
    solid_node.motion answers what moves.

Twelve import lines would make the machine run again. They would not
make it say what the machine is. The same release added `Revolute` and
`Prismatic` — a freedom declared on the body that has it, with its axis
and anchor stated in the PARENT's frame — and `drives`, which says that
one coordinate's motion is another's.

This machine is what those are for. It has three axes and every one of
them today is a `translate` or a `rotate` inside a `simulate()`, reached
through a chain of ports whose only job is to carry a number one level
further down the tree: the machine tells the X stage where its carriage
is, the X stage tells the motor end which way its shaft faces, the motor
end tells the belt side, the belt side turns the pulley. Four ports and
six `simulate()` methods to say "the pulley turns with the belt".

Nothing about the machine changes. Every pose is identical, every
driver, instruction, placement, contract and test is untouched. What
changes is that the drive chain becomes readable: the X pulley pays belt
off at its pitch arc and the carriage goes with it; the Y pulley does the
same to the bed; the screws' angle is what the beam's height is worth.

## What changes

Frames throughout are the machine's own, as the package states them:
X across the machine, Y from the front to the back, Z up, origin at the
middle of the build volume's footprint. Every joint's `axis` and `at`
below is written in the frame the declaring node's PARENT places it in,
which is what makes each of them a reading of a `render()` line that is
already there rather than a new number.

### The joints to declare — 5 declarations, 5 realized freedoms

**1. `XStage.lift` — the whole beam climbs the Z screws.**

    # metamaquina2/x_stage/x_stage.py
    lift = Prismatic(axis=(0, 0, 1), unit='mm')

Today `Metamaquina2.simulate()` writes

    stage = [0, -XZStage_offset,
             BuildPlatform_height + z_screw.lift(self.z) + nozzle_tip_distance]
    self.x_stage.translate(stage)

which is a constant stand plus one moving term. The constant part moves
to `Metamaquina2.render()`, where a rest placement belongs and where the
README already says it belongs:

    #: Where the beam stands with the screws at nought.
    STAGE_REST = [0, -XZStage_offset,
                  BuildPlatform_height + nozzle_tip_distance]

    def render(self):
        self.x_stage.translate(STAGE_REST)
        ...  # the reel and the strand, unchanged

and `lift` is the one moving term: millimetres the beam rises above
`STAGE_REST`. The composed world matrix is `translate(STAGE_REST) ∘
translate([0, 0, lift])`, which is bit-for-bit the vector the single
translate builds today, because the two translations are along different
components of one vector and translations commute.

`simulate()` still needs the whole vector for the filament paragraph, and
it reads it off the same constant:

    stage = [STAGE_REST[0], STAGE_REST[1],
             STAGE_REST[2] + z_screw.lift(self.z)]

so the number is written once and both readings come off it.

**2. `XCarriage.travel` — the carriage slides along the beam.**

    # metamaquina2/x_stage/carriage/x_carriage.py
    travel = Prismatic(axis=(1, 0, 0), unit='mm')

Today `XStage.simulate()` writes `self.carriage.translate(
[self.carriage_position.value - XCarPosition, 0, 0])`. The coordinate is
therefore millimetres the carriage has slid along the beam from the pose
the design's own `XCarPosition` knob draws it at — a displacement, not a
machine coordinate, because the design places the carriage at
`XCarPosition` in `render()` and the axis only ever applied the offset
from there. Naming the displacement keeps `render()` untouched.

**3. `YPlatform.slide` — the bed slides along the Y rods.**

    # metamaquina2/y_axis/platform/y_platform.py
    slide = Prismatic(axis=(0, 1, 0), unit='mm')

Today `YAxis.simulate()` writes `self.platform.translate([0, placed, 0])`
with `placed = self.platform_position.value - XZStage_offset`. Same
reading: millimetres the platform has slid along the machine's +Y from
where `render()` draws it.

**4. `XPulley.spin` — the X motor pulley turns.**

    # metamaquina2/x_stage/ends/motor/belt_side.py, beside PULLEY_DEPTH
    class XPulley(GT2Pulley):
        """The pulley on the X motor shaft: a GT2Pulley that turns on
        the shaft the belt side bolts its motor to."""
        spin = Revolute(axis=(0, 0, 1),
                        at=(XEnd_box_size / 2, XMotor_height, 0.0),
                        unit='deg')

    pulley = XPulley(period=PERIOD, spin=shaft)      # the wiring, below

Today `XEndMotorBeltSide.simulate()` writes `self.pulley.rotate(
self.shaft.value, [0, 0, 1])`, which composes innermost, so it is a turn
about the pulley's own axis at its own placed origin. Numbers: `render()`
puts the pulley at `[XEnd_box_size / 2, XMotor_height, PULLEY_DEPTH]`
with no rotation, so in the belt side's frame the axis is +Z and the
anchor is that placed origin. The along-axis component is written `0.0`
rather than `PULLEY_DEPTH`: the difference between the two points lies
along the rotation axis, where `translate(-a) · R · translate(a)` cancels
it exactly, so the composed matrix is identical and the number that is
about where the pulley sits along its shaft stays in `render()`, which
is the only place that cares.

**5. `YPulley.spin` — the Y motor pulley turns.**

    # metamaquina2/y_axis/motor/y_motor.py, beside the imports
    class YPulley(GT2Pulley):
        """The pulley on the Y motor shaft, standing in the belt's own
        plane rather than the motor's."""
        spin = Revolute(axis=(-1, 0, 0), at=(0.0, SHAFT[0], SHAFT[1]),
                        unit='deg')

    pulley = YPulley(period=PERIOD, spin=shaft)      # the wiring, below

Today `YMotor.simulate()` writes `self.pulley.rotate(self.shaft.value,
[0, 0, 1])`, and `render()` stands the pulley with
`.rotate(90, [1, 0, 0]).rotate(-90, [0, 0, 1]).translate([belt_width / 2
- self.pulley_offset, SHAFT[0], SHAFT[1]])`. The axis is that placement
applied to the part's own +Z: `Rx(90)` carries `(0, 0, 1)` to
`(0, -1, 0)` and `Rz(-90)` carries that to `(-1, 0, 0)`. So in the
motor's frame the pulley turns about the machine's -X, which is the fact
the class docstring currently spends a paragraph explaining ("its local x
lands on the loop's x and its axis on the loop's width"), and the anchor
is the pulley's placed origin with the along-axis component written
`0.0` for the same reason as above. `SHAFT` is already imported by this
module from `y_axis.motor.mount` and is the shaft's `(y, z)` in the
motor's frame.

**No joint has a `range`.** A joint's range is enforced for a numeric
binding, unlike a driver's, and this machine's tests drive `x` and `y` to
`±BuildVolume_X / 2` and `±BuildVolume_Y / 2` exactly and `z` from 0 to
`BuildVolume_Z` exactly — `test_the_carriage_rides_the_x_rods_across_its_travel`,
`test_the_x_ends_ride_the_z_rods_across_the_z_travel`,
`test_every_instruction_lands_on_the_position_it_names`. The maker-facing
travel is already declared, once, on the three drivers, and that is what
the viewer's sliders read. Adding it again on the joints would buy
nothing and could refuse a pose a contract states. (Snappy-reprap's
precedent; flagged under Tests for the orchestrator.)

### The wirings — 2

    # XEndMotorBeltSide
    shaft = RotationalPort(unit='deg')
    pulley = XPulley(period=PERIOD, spin=shaft)

    # YMotor
    shaft = RotationalPort(unit='deg')
    pulley = YPulley(period=PERIOD, spin=shaft)

`shaft` is the motor shaft's own angle and stays a port: it is what the
axis binds, and the pulley is bored onto it, so handing the coordinate
down as a wiring is the sentence the machine wants ("the pulley goes
round with the shaft") and it costs no `simulate()`. Both `simulate()`
methods disappear. It also keeps `belt_side.shaft.value` and
`motor.shaft.value` readable, which two contracts do read (see Tests).

### The relations to state — 9 sentences, both ends named

**On `Metamaquina2`** (`metamaquina2.py`), five sentences replacing three
`connect()` calls and one `translate()`:

    x.drives(x_stage.carriage.travel, offset=-XCarPosition)
    y.drives(y_axis.platform.slide,   offset=-XZStage_offset)
    z.drives(x_stage.lift,            ratio=z_screw.SCALE)
    z.drives(z_axis.bars.angle,       offset=z_screw.PHASE)
    z.drives(z_axis.couplings.angle,  offset=z_screw.PHASE)

* `x` (millimetres of the carriage along the machine's X, in the design's
  own coordinates) drives `x_stage.carriage.travel` (millimetres the
  carriage has slid from the pose `XCarPosition` draws it at). The offset
  is `-XCarPosition`, which is the `- XCarPosition` in today's
  `XStage.simulate()`.
* `y` (millimetres of the bed along the machine's Y) drives
  `y_axis.platform.slide` (millimetres the platform has slid from where
  it is drawn). The offset is `-XZStage_offset`, today's `placed = ... -
  XZStage_offset`: the platform is drawn about the origin and the whole
  X/Z stage sits that far off it.
* `z` (DEGREES the screws are turned — the driver's native value, which
  is what a relation's `Driver` end resolves to and what `simulate()`
  reads today) drives `x_stage.lift` (millimetres the beam rises). The
  ratio is `z_screw.SCALE`, which is exactly `z_screw.lift(turned) =
  turned * SCALE`, the negative lead over 360 that carries the thread's
  handedness.
* `z` (degrees) drives `z_axis.bars.angle` and `z_axis.couplings.angle`
  (degrees each is turned), one for one with the offset `z_screw.PHASE`
  — the turn a builder puts into the screws once, with them in their
  hands, to line their thread up with the nuts. That is today's
  `self.connect(self.z + z_screw.PHASE, self.z_axis.screw)` plus the two
  wires `ZAxis.simulate()` fans it out with; the two relations reach the
  two ports by path and `ZAxis`'s forwarding port and `simulate()` go.

**On `XStage`** (`x_stage.py`), two sentences replacing three lines of
`simulate()` and two paragraphs of docstring about the three ways one
carriage position has to be told:

    end_motor.belt_side.shaft.drives(
        belt.clamp,
        ratio=-x_belt.BEAM_PER_DEGREE,
        offset=x_belt.PULLEY_AT_ORIGIN * x_belt.BEAM_PER_DEGREE)
    end_motor.belt_side.shaft.drives(
        carriage.travel,
        ratio=-x_belt.BEAM_PER_DEGREE,
        offset=(x_belt.PULLEY_AT_ORIGIN * x_belt.BEAM_PER_DEGREE
                + x_belt.CLAMP_ORIGIN - XCarPosition))

* `end_motor.belt_side.shaft` (degrees of the X pulley about the belt
  plane's +Z) drives `belt.clamp` (millimetres ALONG THE BEAM from the
  tangent point where the upper run leaves the pulley — the port's own
  declared `scale` is what turns that into millimetres of belt across the
  run's slight tilt, and it is applied by the binding, as it is today).
* the same shaft drives `carriage.travel` (millimetres from the drawn
  rest). The clamp's origin and the drawn rest are the only difference
  between the two, hence the one extra term.

**On `YAxis`** (`y_axis.py`), two more replacing three lines:

    motor.shaft.drives(
        belt.clamp,
        ratio=y_belt.BED_PER_DEGREE,
        offset=-y_belt.PULLEY_AT_ORIGIN * y_belt.BED_PER_DEGREE)
    motor.shaft.drives(
        platform.slide,
        ratio=-y_belt.BED_PER_DEGREE,
        offset=(y_belt.PULLEY_AT_ORIGIN * y_belt.BED_PER_DEGREE
                - y_belt.CLAMP_ORIGIN))

* `motor.shaft` (degrees of the Y pulley about the machine's -X) drives
  `belt.clamp` (millimetres along the loop's own x from the tangent point
  on the rear idler, scaled by the port as before), and drives
  `platform.slide` (millimetres of bed along +Y). The two signs differ
  because the loop's x runs from the rear of the machine forwards,
  against the machine's y — today's `-placed`, now one minus sign in one
  ratio instead of a negation threaded through three lines.

**Where the ratios come from.** Two constants per belt module, both
derived from numbers already in the module and both named for what they
are:

    # metamaquina2/x_stage/x_belt.py, after pulley_angle()

    #: Millimetres of belt per degree of pulley: the pitch arc.
    PITCH_ARC = math.pi * (PULLEY_RADIUS + gt2.PITCH_LINE) / 180

    #: What a degree of pulley is worth along the beam -- the pitch arc
    #: read back through the clamped run's own tilt, which is the port's
    #: own scale.
    BEAM_PER_DEGREE = PITCH_ARC / gt2.span_scale(CIRCLES, CLAMP_SPAN)

    #: Which way the pulley faces with the clamp at nought.
    PULLEY_AT_ORIGIN = pulley_angle(CLAMP_ORIGIN)

and the same three in `y_belt.py` with `BED_PER_DEGREE`. `pulley_angle()`
itself is kept, unchanged, and is what `PULLEY_AT_ORIGIN` is read off, so
no arithmetic is retyped: the phase is the existing function evaluated at
the one position where the anchor is nought, and the rate is the same
`span_scale / (PULLEY_RADIUS + PITCH_LINE) · 180/π` that function
divides by. Every relation here is an `Affine`, so it inverts itself and
the chain solves backwards from the end the drivers bind — which is what
this machine needs, because the belt is drawn from the carriage while the
pulley drives it.

**How it solves.** The root binds `carriage.travel` and
`platform.slide`; an ancestor's relation is solved before its
descendant's, so when `XStage`'s two relations run, `carriage.travel` is
already bound. The second inverts to give `shaft`; the first then runs
forward to give `belt.clamp`; the wiring on the belt side carries `shaft`
into `pulley.spin`. Order within the class does not matter — the solver
propagates repeatedly until nothing changes — but the sentences are
written pulley-first because that is the machine.

### Derived coordinates

**None.** No coordinate here is a sum or difference of two others: the
three axes are independent and each drive is a chain, not a
differential. Said explicitly because a reviewer will look for one.

### The ports

**Removed — four, every one a forwarder.**

* `XStage.carriage_position` — carried `x` one level down to a
  `translate`. The root now reaches `x_stage.carriage.travel` by path.
* `YAxis.platform_position` — the same for the bed.
* `ZAxis.screw` — took the screw angle and fanned it to two children.
  The root now reaches `z_axis.bars.angle` and `z_axis.couplings.angle`
  by path, and `ZAxis.simulate()` goes with it.
* `XEndMotor.shaft` — took the pulley's phase and handed it to
  `belt_side`, deriving nothing, as its own docstring says. `XStage`'s
  relation reaches `end_motor.belt_side.shaft` by path, and
  `XEndMotor.simulate()` goes with it.

**Kept — seventeen, every one read by something.**

* `XBelt.clamp`, `YBelt.clamp` — molejo shape parameters. The loops are
  not placed, they are redrawn from wherever the clamp holds the belt,
  and `Wrap(anchor={'span': ..., 'at': P.clamp})` reads the port. Driven
  by a relation now instead of a `connect()`, which is the honest
  statement: the pulley pays belt off and the rubber travels.
* `Filament.over_x`, `over_y`, `head_x`, `head_y`, `plane` — the five
  places the free run is pinned, every one a molejo `P.` reference.
  These stay bound by `connect()` in `Metamaquina2.simulate()`. Each is
  affine in one or two drivers and could be five relations, but only by
  scattering into module constants one paragraph that names three
  intermediates (`stage`, `entry`, `strand_origin`) and shares them
  across all five, and by restating `in_strand_frame`'s permutation five
  times. This is the documented driver → port → geometry chain for a
  flexible part, not a transmission, and it stays.
* `IdlerSpring.height` ×2 and `BedSpring.height` ×4 — molejo shape
  parameters, bound from a constant in `Handle.simulate()` and
  `BedLevelScrew.simulate()`. Nothing drives them: the lever is squeezed
  by hand and the bed is levelled with a screwdriver, and the machine has
  no state for either. Not transmissions, and not touched.
* `ZBars.angle`, `ZCouplings.angle` — the screw angle each assembly turns
  its two `.repeat()` children by. These stay ports feeding two
  hand-written loops; see Known gaps 1.
* `XEndMotorBeltSide.shaft`, `YMotor.shaft` — the motor shafts' own
  angles, bound by their axis and handed to their pulley as a wiring.
  Not forwarders: the coordinate is the shaft's, and the wiring is what
  replaces a `simulate()`.

### The `simulate()` methods

* `Metamaquina2.simulate()`: 15 statements to 10. The `x_stage.translate`
  and the three `connect`s into `carriage_position`, `platform_position`
  and `screw` go. The filament paragraph stays whole, reading `stage`
  off `STAGE_REST` as above.
* `XStage.simulate()`: **gone**. Its three statements are the two
  relations.
* `YAxis.simulate()`: **gone**. Same.
* `ZAxis.simulate()`: **gone**, with its port.
* `XEndMotor.simulate()`: **gone**, with its port.
* `XEndMotorBeltSide.simulate()`: **gone**, replaced by the joint and the
  wiring.
* `YMotor.simulate()`: **gone**, same.
* `ZBars.simulate()`, `ZCouplings.simulate()`: unchanged, 2 lines each
  (Known gaps 1).
* `Handle.simulate()`, `BedLevelScrew.simulate()`: unchanged.

Six `simulate()` methods disappear; none is added.

### Frame arithmetic that leaves

No inverted transform leaves — this package never wrote one, because
every hand-written rotation is about a part's own placed origin. What
leaves is the rest of the same tax: two signed rotations whose sign and
frame exist only because a placement turned the part, the negation of
`placed` threaded through three lines of `YAxis.simulate()`, and four
docstring paragraphs that exist only to justify them — "the loop's x runs
from the rear of the machine forwards, against the machine's y", "its
local x lands on the loop's x and its axis on the loop's width", "motion
composes innermost, so this turn goes on before the three operations that
stand the pulley", and the X stage's "the pulley is told it a third way".
Each of those becomes an `axis=` or a `ratio=` in a sentence a reader can
check against the machine.

## What does not change

* The three drivers `x`, `y`, `z` — their units, defaults, ranges and
  `scale` — and the four instructions `Rest`, `CenterX`, `PresentBed`,
  `HomeZ` with their durations. The viewer's control surface is
  untouched.
* The two declared parameters `spool_holder_offset` and
  `power_supply_fitted`.
* Every `render()` except one added line on the root: every placement,
  orientation, standoff, bolt station and repeat, in all seventy
  modules. The one added line is the constant part of a translate moved
  out of `simulate()`, and it composes to the same matrix.
* Every number in `params.py`, `z_screw.py`, `gt2.py`, `x_belt.py`,
  `y_belt.py` and every module constant. `pulley_angle`, `z_screw.angle`,
  `z_screw.lift`, `gt2.span_scale`, `gt2.stations` keep their bodies; the
  two belt modules only gain three derived constants each.
* Every geometry class, every `.scad` and `.dxf` source read, every
  colour and material. `GT2Pulley` itself is not touched: the two
  subclasses add a joint and nothing else.
* The eight OpenSpec capabilities (`assembly-tree`, `belt-drive`,
  `filament-path`, `hot-end`, `machine-motion`,
  `openscad-design-reading`, `spring-loading`, `z-screw-drive`). **This
  change proposes no spec delta**: the specs describe what the machine
  does and what fits what, not how the package states it, and every
  requirement in them holds word for word afterwards.
* `metamaquina2/test_metamaquina2.py` — see Tests.

## Known gaps

**1. A joint cannot be anchored where the parent places the child, and
here it blocks the four turning Z parts.** `ZBars` holds
`bars = ThreadedRod(length=Z_bar_length).repeat(2)` and stands them at
`[±offset, -XZStage_offset, BAR_BASE]`; `ZCouplings` holds
`couplings = ShaftCoupling().repeat(2)` the same way. Each turns about
its own placed origin, so a joint's `at` would be `(±offset,
-XZStage_offset, BAR_BASE)` — a number that belongs to the PARENT and
differs between two copies of one declaration. Three recorded limits meet
on it at once: the anchor is the child's own placed origin, which the
framework cannot name; the two classes are shared hardware
(`ThreadedRod` is also the frame's four horizontal bars, in
`front_bars.py` and `rear_bars.py`), so the number would have to be
carried inside the hardware module; and the children are `.repeat()`
copies, which a relation cannot fan out over and which no per-copy
anchor can be given. Subclassing to carry the joint would mint a second
cached artifact of a `Z_bar_length` exact ISO thread, the most expensive
leaf in this machine, for geometry that is identical. The
sentences the project wants:

    bars = ThreadedRod(length=Z_bar_length).repeat(
        2, turn=Revolute(axis=(0, 0, 1), at=(side * offset, -XZStage_offset, BAR_BASE)))
    z.drives(bars.turn, offset=z_screw.PHASE)

a joint given at the declaration site with its anchor resolved against
the DECLARING parent's parameters (recorded candidate fix (b)), and a
relation that fans out over a repeated child. Nth sighting of both
recorded gaps. So `ZBars.angle` and `ZCouplings.angle` stay ports and
their two `for` loops stay: four rotations out of nine freedoms.

**This does not defer the project.** The Z axis's principal motion is the
beam climbing, and that IS a joint — `XStage.lift`, driven from `z` at
the screws' own lead. The bars and the couplings are dressing turning
under it, exactly as the Prusa i3's Z screws are, and a later
declaration-site primitive ADDS two sentences rather than redoing the
refactor.

**2. Shared catalogue classes need a subclass to carry a joint.**
`GT2Pulley` is on two motors with two different placements, so the two
pulleys need `XPulley` and `YPulley`, three-line subclasses whose entire
content is one `Revolute`. The same finding's milder half, recorded
twice already (poseidon, OpenMANIPULATOR-X). Ceremony, not hand-written
motion; not a deferral. Cost is two cache identities rebuilt once (see
Tests, item 3).

**No new framework gap, and NO DEFERRAL is recommended.**

* **No body here has more than one freedom.** The beam climbs and the
  carriage on it slides, but those are two bodies, one nested in the
  other, and their motions are the framework's ordinary nesting rather
  than two joints on one body. Each pulley turns and nothing else. The
  composition-order gap that defers OpenCycloid, the hexapod, the dog,
  the Internal Cycloidal Actuator and the Mini Kossel does not arise
  here.
* No orbit, no free joint, no path, no multi-source relation, no
  per-copy law. Every one of the nine freedoms is one coordinate on one
  axis, and every transmission is affine.
* No `Length`-token arithmetic reaches a ratio or an anchor: every number
  above is a plain float out of `params.py` or a module constant, so the
  Pascaline's `DimensionError` sighting does not bite. (`Length` appears
  on `spool_holder_offset`, `hot_end_bolt` and `shaft_length`, none of
  which is in a relation.)

**Two things the model does not do, which this change does not invent.**

* **The extruder has no drive.** There is no `e` driver on this machine.
  `Extruder` has no `simulate()`: the hobbed bolt, the big and small
  gears, the two 608 bearings and the stepper are all placed at rest in
  `render()` and none of them turns. The one extruder-side motion is the
  free run of filament, which is redrawn from where the head stands —
  the five molejo ports above. Giving the machine an `e` driver and
  turning the gear train off it is a real and attractive change, and it
  is a change to what the machine DOES; it does not belong in a
  refactor whose acceptance is that no pose moves.
* **The idlers do not turn.** The X idler (`XIdlerPulley`, a 608 on a
  shaft) and the Y belt's three bar idlers are placed and never rotated
  today. Two contracts already check the belt rides them without biting;
  none checks a phase. No joint is declared for them.

## Pre-existing state

`git status` on `main` is **clean**: no modified, staged or untracked
files (`_build/`, `_build.lock`, `.pytest_cache/` and
`__pycache__/` are ignored). There is nothing for stage 0 to commit; the
implementer should confirm it and go straight to stage A. Do not touch
`_build/` — a stale artifact tree there is the cache and is not evidence.

## Tests

One test module, `metamaquina2/test_metamaquina2.py`, one class
`Metamaquina2Test`, **67 tests**, all against the one declared model
(`pyproject.toml` names `metamaquina2.metamaquina2:Metamaquina2`; there
are no plain `pytest` tests and no second root). It imports no name that
moved, so stage A does not touch it. Roughly: the carriage and platform
riding their rods and the X ends riding the Z rods across the travels;
the three axes moving what they should and nothing else; both belts as
flexible leaves, closed loops, redrawn where they stand, teeth travelling
with the carriage and the bed, riding their idlers without biting; both
pulleys meshing with their belts, straddling them, and turning one groove
per belt tooth; the six springs; the hot end's stack and the nozzle tip
where Z is measured from; the filament's wound layer, its free run and
its clearances; the rest pose, the four instructions and the Z homing
rate; the Z nuts threaded on wherever the screws are turned; and the
integrity sweeps.

**Expected to need a change: none.** Flagged, for the orchestrator to
decide, not the implementer:

1. **Two contracts read a port this change keeps — deliberately.**
   `test_the_x_pulley_turns_one_groove_per_belt_tooth` reads
   `belt_side.shaft.value` (lines 817–825) and
   `test_the_y_pulley_turns_one_groove_per_belt_tooth` reads
   `motor.shaft.value` (lines 925–933). Keeping `shaft` as a port and
   wiring it into the pulley's joint is partly why that shape was
   chosen: both reads stay valid and neither test is touched. The
   alternative — dropping both ports and letting `XStage`/`YAxis` reach
   `…pulley.spin` by path — is one line shorter per axis and would make
   those two reads `belt_side.pulley.spin.value` and
   `motor.pulley.spin.value`, i.e. a test edit. If the orchestrator
   prefers the shorter form, that is the trade, and it is a decision
   about tests, not mine.
2. **Sub-ulp pose deviation on the two pulleys.** The X and Y shaft
   angles are the one arithmetic genuinely restated: today one call to
   `pulley_angle(position)`, after this an affine inverted by the solver
   with the same rate and the same phase. The two agree exactly in real
   arithmetic and may differ in the last bit of a float — below 1e-13
   degrees, which is below 1e-14 mm at a 4.839 mm pitch radius. Both
   turning tests use `delta=self.PLACED`, and the two meshing tests
   assert a clearance measured in hundredths of a cubic millimetre, so
   this is a line in the pose comparison to explain, not a failure. If
   either goes red the ratio or offset in this proposal is wrong:
   report it and fix the constant, do not touch the test.
3. **Two leaves get new class names.** `XPulley` and `YPulley` are new
   identities, so their cached artifacts are rebuilt once. No test
   asserts a class name; `test_each_motor_pulley_is_the_one_the_bill_of_materials_buys`
   and `test_each_motor_pulley_straddles_the_belt_it_drives` read
   `TEETH`, `WIDTH` and `GT2Pulley.CLEARANCE`, all inherited unchanged.
4. **Joint ranges are deliberately absent** (see joints above). If the
   orchestrator wants them declared, the poses that would sit exactly on
   a bound must be checked first — `POSES`-style sweeps in
   `test_the_carriage_rides_the_x_rods_across_its_travel` and
   `test_the_x_ends_ride_the_z_rods_across_the_z_travel` reach the
   declared travel ends exactly, and `test_every_instruction_lands_on_the_position_it_names`
   lands on `-BuildVolume_Y / 2` and `z = 0`.
5. **Standalone builds of `XStage`, `YAxis` and `ZAxis` change
   character.** Today each refuses to build without its port connected
   ("an unconnected port has no value"), which their docstrings state as
   a feature. After this, an unbound joint simply does not move, so
   `XStage` and `YAxis` would build at rest instead of raising.
   `ZBars`/`ZCouplings` keep their ports and keep refusing. No test
   builds any of them standalone — the suite builds only the root — and
   the three docstrings will be corrected to say what is now true. If
   the orchestrator wants the refusal preserved, it is a rest-default
   `if … is None` in each class, openarm's shape; say so and it will be
   added.
6. **The baseline is unknown.** This suite has not been run against this
   framework tree, and it is the largest in the catalogue (67 contracts
   over a whole printer, including exact-thread nuts and two molejo
   belts). Stage A establishes it; anything red at stage A stays red at
   stage B and is not this change's business. Run one suite at a time.
