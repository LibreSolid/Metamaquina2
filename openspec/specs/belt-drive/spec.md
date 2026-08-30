# Belt Drive Specification

## Purpose

Give both driven axes the toothed drive they really run: GT2 belts drawn
as flexible parts whose rubber is dragged through a standing loop by the
thing clamped to them, and on each belt motor the pulley the bill of
materials buys, meshed with its belt at every position the axis reaches.

## Requirements

### Requirement: Each driven axis carries its belt as a flexible part
The X stage and the Y axis SHALL each carry their GT2 belt as a flexible
leaf: a single closed watertight loop, toothed at the standard's own
pitch and tooth form, wrapped around the circles the design runs it on,
with the loop's dimensions read from the design as everything else is. A
deliberate correction of a design literal (the Y loop's height, the belt
line's radius at a pulley) SHALL be derived from the design's own
numbers rather than written down.

#### Scenario: The document holds two belts
- **WHEN** the machine is built
- **THEN** the X and Y belts are flexible leaves of the axes that run
  them, each one closed loop of toothed band

### Requirement: A belt is redrawn where it stands, never re-placed
Driving an axis SHALL NOT move its belt: both ends of each loop are
bolted down, so the loop keeps its position and shape while the rubber
inside it travels. The belt SHALL be redrawn from the same position its
axis places the carriage or bed with, so the teeth travel exactly with
the thing clamped to the belt: a whole tooth of travel redraws the belt
identically, half a tooth moves a crest to a root and no further.

#### Scenario: An axis is driven
- **WHEN** the X or Y driver is displaced
- **THEN** the belt's bounds do not move, and its tooth pattern has
  advanced along the loop by exactly the displacement

### Requirement: A belt rides its idlers without biting them
Each belt SHALL clear every bare bearing it runs on: the X belt sits on
its idler bearing, and the Y belt lies flat on its three bar bearings on
its smooth back, teeth facing away from the bare races.

#### Scenario: The loops are swept
- **WHEN** either belt is compared against the bearings it rides
- **THEN** the belt touches down on each bearing's running surface and
  cuts no volume out of any of them

### Requirement: Each belt motor carries the pulley the bill of materials buys
Both belt motors SHALL carry the bought GT2 pulley (16 teeth, 6 mm), its
belt-facing dimensions derived from the tooth count and the GT2 tooth
form rather than from the design's radius literal, placed straddling the
belt it drives in the belt's own running plane, its grooves relieved so a
tooth can enter and leave.

#### Scenario: A pulley stands across its belt
- **WHEN** either motor's pulley is compared with its belt
- **THEN** the pulley spans the belt's width in the belt's plane, and the
  Y pulley is bored onto its motor shaft

### Requirement: Belt and pulley mesh, and turn together
The X belt SHALL be meshed on its motor pulley and the Y belt SHALL be
threaded between its rear bar bearings and reverse-bent over its pulley,
toothed face against the metal. At every phase of a tooth the meshed
teeth SHALL sit in the pulley's grooves with clearance and without
interference, and driving the axis SHALL turn the pulley exactly one
groove per tooth of belt travel, in the direction the mesh dictates,
identically in every evaluator the shape is published to.

#### Scenario: The mesh is swept through a tooth
- **WHEN** the axis is driven through one tooth of travel in phases
- **THEN** the belt grazes nothing, stays within its clearance of the
  grooves, and the pulley has turned exactly one groove

### Requirement: Belts travel to the viewer as shapes
Each belt SHALL be published to viewers as its parametric shape, with
parameters naming the machine's own drivers, rather than as a mesh per
position, so a viewer redraws it at frame rate as the axis moves.

#### Scenario: A viewer follows a moving axis
- **WHEN** a published driver value changes in a viewer
- **THEN** the viewer re-evaluates the belt's shape itself, with the
  same result the Python evaluator draws
