# spring-loading Specification

## Purpose

Draw the parts this machine holds against something with a spring -- the
heated bed a maker levels, the idler that presses filament onto the hobbed
bolt -- as flexible leaves whose length is the room the parts around them
leave, with the wire and the coil count derived from the catalogue line the
design buys them by rather than invented.

## Requirements
### Requirement: The bed stands on four springs
The heated bed SHALL be held off the Y platform by four compression springs,
one at each of the four corner holes the design cuts through both the bed
board and the platform sheet, each with the M3 bolt, the three M3 washers and
the nut the bill of materials buys to hold it. Each spring SHALL travel with
the bed.

#### Scenario: The bed is looked at from underneath
- **WHEN** the assembly is built
- **THEN** four springs stand between the platform sheet and the heated bed
  board, each on the axis of a hole through both of them, and a bolt runs
  down through each of them to a nut under the platform

#### Scenario: The bed is driven along its rods
- **WHEN** the Y driver is displaced
- **THEN** each bed spring moves with the bed by that displacement

### Requirement: The idler is pressed onto the filament by two springs
The extruder handle's two long bolts SHALL each carry a compression spring
with the M4 washer the bill of materials buys for it, seated on the outer
face of the idler's back plate so that compressing it presses the idler
bearing onto the filament rather than away from it.

#### Scenario: The extruder is looked at from the front
- **WHEN** the assembly is built
- **THEN** two springs stand on the handle's bolts, each seated through its
  washer on the far face of the idler back plate and running towards the
  bolt head, and neither cuts into the plate it stands on

### Requirement: A spring's length is the space its neighbours leave
Every spring SHALL be a flexible leaf: its length SHALL arrive through a
declared port, and the assembly holding it SHALL bind that port from the
positions it places the spring's neighbours at, never from a length written
down a second time. Where the design states a length for the same gap and
that statement disagrees with where the design's own parts stand, the
placements SHALL win and the disagreement SHALL be recorded where the
binding is made.

#### Scenario: A spring is measured against what it stands between
- **WHEN** a spring and the two parts it bears on are compared
- **THEN** the spring reaches from one to the other, touching both and
  cutting into neither

#### Scenario: The design's own spring length is compared with the gap
- **WHEN** the heated bed's installed spring length is compared with the
  design's `heatedbed_spring_compressed_length`
- **THEN** the two differ by the same amount as the design's two statements
  of the platform deck height, and the drawn spring follows the gap

### Requirement: Wire and coil count are derived from the part that is bought
The bill of materials names a spring only by an outside diameter and a free
length. The wire thickness SHALL be derived as what leaves a declared
clearance between the coil's bore and the shank the spring is threaded on,
and the coil count SHALL be the most whole turns that still leave a clear
wire diameter between consecutive coils at the length the spring is
installed at. Neither SHALL be written down as a literal.

No spring SHALL be drawn longer than the free length it is bought at. A
spring whose neighbours leave it less room than that SHALL be drawn
compressed to the room they leave; a spring the design gives no setting
for SHALL be drawn at its free length rather than at an invented preload,
and the adjustment the design leaves for it SHALL be recorded.

#### Scenario: A spring is threaded on its bolt
- **WHEN** a spring and the bolt running through it are compared
- **THEN** the bolt passes through the coil without touching it, at the
  declared clearance

#### Scenario: A spring is measured at its installed length
- **WHEN** a spring is built at the length its assembly binds
- **THEN** consecutive coils clear each other by at least the wire's own
  diameter, and the spring is no longer than the free length the bill of
  materials buys

#### Scenario: The bed's springs are compared with their free length
- **WHEN** a bed spring's installed length is compared with its free length
- **THEN** it is shorter, so the spring is under load and the corner it
  holds can be levelled against it

### Requirement: A spring is one closed watertight body
Each spring SHALL come out of its evaluator as a single closed band of wire,
watertight and in one piece, at every length its port can carry.

#### Scenario: A spring is swept
- **WHEN** a spring's mesh is inspected
- **THEN** it is watertight, in one piece, and of positive volume

### Requirement: Springs travel to the viewer as shapes
Each spring SHALL be published to viewers as its parametric shape with an
expression for its length, as the belts are, rather than as a mesh per
length, so a viewer that later drives the bed's level or the idler's release
redraws the spring itself.

#### Scenario: The document is serialized
- **WHEN** the machine is serialized
- **THEN** every spring appears as a flexible shape with one published
  parameter, and no spring appears as a mesh reference

