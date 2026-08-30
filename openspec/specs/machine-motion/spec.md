# Machine Motion Specification

## Purpose

Put the machine's motion in front of whoever opens it: three drivers on
the root in the machine's own millimetre coordinates, moving exactly what
the machine moves, with instructions for the poses a maker reaches for.

## Requirements

### Requirement: The three axes are drivers on the machine root
The root SHALL declare drivers `x`, `y`, and `z`, read and set in
millimetres in the design's own coordinates, whose defaults are the
design's own rest-pose knobs (`XCarPosition`, `YCarPosition`,
`ZCarPosition`) and whose ranges are the advertised build volume. An
untouched machine SHALL render exactly the machine the design has always
drawn.

#### Scenario: The machine opens at rest
- **WHEN** the model is built with no driver touched
- **THEN** every leaf lands on the same world bounds the design's own
  rendering places it at

#### Scenario: A maker reads the axis ranges
- **WHEN** the drivers are inspected
- **THEN** X and Y range over half the build volume either side of
  centre, and Z from the build surface to the full build height, all in
  millimetres

### Requirement: Each driver carries its load and nothing else
Driving X SHALL slide the carriage along its beam, driving Y SHALL slide
the bed on its rods, and driving Z SHALL raise or lower the whole X beam
and everything riding it. The frame and the other axes SHALL NOT move,
and the placement contracts SHALL hold at every position of the travel.

#### Scenario: X moves the carriage
- **WHEN** the X driver is displaced
- **THEN** the carriage's bounds move by that displacement and the frame
  beside it does not move

#### Scenario: Y moves the bed
- **WHEN** the Y driver is displaced
- **THEN** the platform's bounds move by that displacement and only the
  platform's

#### Scenario: Z moves the beam
- **WHEN** the Z driver is displaced
- **THEN** the whole X stage, carriage included, moves by that
  displacement while staying hung on the Z rods

### Requirement: Z's state is the screws' own angle
The Z driver SHALL hold the screws' angle in degrees and declare the
scale that makes it millimetres of beam: negative, one M8 lead per turn,
because a right-handed thread lifts a captive nut when turned clockwise
seen from above. Every maker-facing surface -- slider, readout,
instruction targets -- SHALL stay in millimetres.

#### Scenario: A maker never sees degrees
- **WHEN** the Z driver is shown or set through its maker-facing surface
- **THEN** the value is millimetres of nozzle height above the build
  surface

#### Scenario: The bars are worth the height
- **WHEN** the beam rises a quarter of the thread's lead
- **THEN** the driver's state has turned each bar exactly minus ninety
  degrees

### Requirement: Instructions land on the positions they name
The root SHALL offer `Rest` (all three axes back to the design's drawn
pose), `CenterX` (carriage to the middle of the bed), `PresentBed` (bed
forward to where a finished print is reached), and `HomeZ` (beam wound
down until the nozzle meets the build surface). Each instruction SHALL
arrive at exactly the position its name says. Instructions that move Z
SHALL take the time a screw takes: the declared travel at the Z homing
feedrate, not an animation's convenience.

#### Scenario: An instruction is stepped through a simulation
- **WHEN** any instruction runs to completion
- **THEN** each named axis stands at the instruction's target value

#### Scenario: Homing Z takes a screw's time
- **WHEN** `HomeZ` runs
- **THEN** the beam reaches the build surface after the whole declared
  travel at 4 mm/s, with the bars visibly turning all the way down
