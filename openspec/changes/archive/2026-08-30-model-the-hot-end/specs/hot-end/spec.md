## ADDED Requirements

### Requirement: The extruder carries a hot end of the parts the bill of materials buys
The extruder SHALL carry a hot end assembly holding, as separate leaves, the
PEEK nozzle holder, the PTFE liner, the brass nozzle, the heater resistor and
the thermistor -- the five parts the bill of materials buys for it -- and the
extruder SHALL carry the two M3x30 the design cuts holes for to hold it.

#### Scenario: The hot end is looked at from below
- **WHEN** the machine is built
- **THEN** the extruder carries a hot end of five parts, held by two M3x30
  bolts standing in the holes the extruder's own slices are cut with

### Requirement: The nozzle tip stands where the machine measures Z from
The drawn nozzle tip SHALL stand `jhead_length - jhead_instalation_depth`
below the face the extruder clamps the holder against, so that it is
`ZCarPosition` above the build surface at rest and meets the build surface
when Z is homed. The one dimension the holder's drawing declares free -- its
length, "36.5mm or 50mm (length not critical)" -- SHALL be what makes that
true, rather than a length written down beside a tip that lands somewhere
else.

#### Scenario: The machine is homed
- **WHEN** `HomeZ` runs to completion
- **THEN** the nozzle tip has come down onto the build surface, touching the
  glass and cutting into nothing

#### Scenario: The nozzle is measured against the design's own constant
- **WHEN** the drawn tip is measured from the holder's shoulder
- **THEN** it stands at the design's own `jhead_length` less its
  `jhead_instalation_depth`

### Requirement: The stack is the stack a builder assembles
The holder SHALL stand its 5/8" shoulder against the extruder's underside
with its collar and neck inside the block; the nozzle SHALL be screwed into
the holder's foot until its heater block meets the holder's shoulder; and the
liner SHALL run from the holder's top face down the bore to the top of the
nozzle's threaded stub, with its drill point nosing into the melt chamber.
No two of them SHALL share metal.

#### Scenario: The assembly is taken apart
- **WHEN** each pair of hot end parts is compared
- **THEN** each stands against the next without cutting into it, and the
  holder's installed depth is the design's own `jhead_instalation_depth`

### Requirement: The bore is derived from what has to pass down it
The holder's filament bore SHALL be derived from the groove root the design
draws its own body around and the minimum wall the drawing leaves at a
groove, and the liner SHALL pass down it with clearance. Neither the bore nor
the liner's length SHALL be written down as a literal: the length is the room
the holder's top face and the nozzle's stub leave, and where the design
states a different length for the same room, the placements SHALL win and the
disagreement SHALL be recorded where the derivation is made.

#### Scenario: The liner is threaded down the holder
- **WHEN** the liner and the bore it fills are compared
- **THEN** the liner runs the whole bore without cutting into the holder,
  and the clearance is the one the derivation leaves

#### Scenario: The design's own liner length is compared with the room
- **WHEN** the drawn liner is compared with the 47 mm `PTFE_liner.scad` draws
- **THEN** the drawn liner is shorter by exactly what the holder's derived
  length and the nozzle's own stub leave it

### Requirement: The heater and the sensor sit in the holes the nozzle is drilled for
The heater resistor SHALL sit in the heater hole the nozzle module drills
through its block and the thermistor SHALL sit in the thermistor hole, each
coaxial with its hole and neither cutting into the block, with a stated slip
fit rather than a coincident surface.

#### Scenario: The block is sectioned
- **WHEN** the resistor and the thermistor are compared with the block
- **THEN** each stands in its own drilled hole, clear of the brass, and
  reaches out of it far enough to be wired

### Requirement: The hot end is drawn from the design and its own drawings
The nozzle SHALL be the design's own `v4nozzle()` module. The holder, the
liner, the resistor and the thermistor -- which the design does not draw, or
draws only as a dimensioned outline, or draws in a file OpenSCAD cannot parse
-- MAY be drawn here, from the dimensioned shop drawings the repository
carries and from the design's own module-body values, with every departure
recorded where it is made.

#### Scenario: A part of the hot end is asked where it comes from
- **WHEN** the hot end's parts are inspected
- **THEN** the nozzle is the design's module, and every dimension of every
  other part is either a probed design value, an annotated module-body value,
  a number off one of the two shop drawings, or derived from those and
  recorded
