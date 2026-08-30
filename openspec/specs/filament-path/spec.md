# filament-path Specification

## Purpose

Draw the stock this machine consumes: the outermost layer of it lying wound on
the reel beside the machine, and the free run from there over the frame and
into the mouth of the filament channel the extruder is cut with -- one strand,
whose run is redrawn wherever the print head goes and whose end is where the
drawn machine stops leaving room for it.

## Requirements
### Requirement: The reel carries its outermost layer as drawn stock
The reel SHALL be drawn as two things rather than one: the wound tube the
design draws, and its outermost layer, drawn as a single strand of the stock
diameter the design names. The tube SHALL be what is wound under that layer,
so that the two together reach the reel's own outside diameter exactly. The
layer SHALL lie on the tube: its turns SHALL reach the surface the tube is
drawn to, and SHALL neither stand off it nor run inside it.

#### Scenario: The loaded stand is looked at from the end
- **WHEN** the assembly is built
- **THEN** the strand lying on the reel runs at one radius about the reel's
  own axis, and its outside reaches the design's reel diameter

#### Scenario: The layer is measured against the tube it lies on
- **WHEN** the radius the layer's turns run at and the radius the tube is
  drawn to are compared
- **THEN** the turns reach that surface and stand no further out than the
  drawing's own section resolves, and the tube is one stock diameter smaller
  on the radius than the design's reel

### Requirement: The layer is as many whole turns of stock as the reel holds
The wound layer SHALL be laid at the stock's own diameter, which is the pitch
a layer on a reel is wound at, and SHALL be the most whole turns of it that
fit within the reel's width. Neither the pitch nor the turn count SHALL be
written down as a literal.

#### Scenario: The layer is measured across the reel
- **WHEN** the strand's turns are counted and measured
- **THEN** consecutive turns are one stock diameter apart, the whole layer
  lies within the reel's width, and one more turn would not fit

### Requirement: The strand runs from the reel to where the machine takes it in
The strand SHALL leave the wound layer tangentially at the top of the reel,
heading towards the machine, and SHALL continue as one unbroken run to the
mouth of the filament channel the design cuts up through the extruder. It
SHALL arrive along that channel, so that what is drawn could be pushed down
it.

#### Scenario: The machine is looked at at rest
- **WHEN** the assembly is built
- **THEN** the strand leaves the top of the reel, crosses to the machine and
  ends at the mouth of the extruder's filament channel, on the axis the
  design cuts that channel on

#### Scenario: The arrival is measured against the channel
- **WHEN** the last of the run is compared with the channel it ends at
- **THEN** the run arrives along the channel's own axis rather than across it

### Requirement: The free run gets over the machine rather than through it
The stand is beside the machine and the extruder is inside it, so the free run
SHALL be carried over the machine clear of everything the frame stands in its
way, and SHALL come down into the channel through the opening the frame leaves
for the carriage to travel in. It SHALL share metal with no part of the frame
or of the beam, at any position the machine's drivers can reach.

#### Scenario: The run is measured against the machine it crosses
- **WHEN** the strand and the parts of the frame and the beam are compared, at
  rest and at both ends of both travels
- **THEN** the run shares metal with none of them

### Requirement: The free run follows the print head
The strand SHALL be a flexible leaf: the two places the free run is pinned —
where it crosses the machine, and where it ends — SHALL arrive through declared
ports, and the machine SHALL bind both from the frame it owns and from where it
puts its own extruder, rather than from positions written down a second time.
Driving the machine SHALL redraw the run between its crossing and its end, and
SHALL leave both the crossing and the wound layer where they are, because
neither the frame nor a reel moves when a print head does.

#### Scenario: The carriage is driven along the beam
- **WHEN** the X driver is displaced
- **THEN** the end of the run moves with the extruder by that displacement,
  the run between the crossing and the end is a different shape, and neither
  the crossing nor the turns lying on the reel have moved

#### Scenario: The beam is driven up its screws
- **WHEN** the Z driver is displaced
- **THEN** the end of the run rises with the extruder, the run between the
  crossing and the end is a different shape, and neither the crossing nor the
  turns lying on the reel have moved

### Requirement: The strand is one continuous piece of stock
The strand SHALL come out of its evaluator as a single closed body,
watertight and in one piece, at every position the machine's drivers can
reach.

#### Scenario: The strand is swept
- **WHEN** the strand's mesh is inspected, at rest and across the travel
- **THEN** it is watertight, in one piece, and of positive volume

### Requirement: The run ends where the drawn machine stops leaving room for it
The run SHALL be drawn only as far as the channel's mouth. Where the drawn
machine leaves no room for stock at or below that mouth, each such place SHALL
be recorded where the run ends and asked for by contract, so that a later
change to the design or to the hot end cannot make one of them quietly go
away.

#### Scenario: The pinch the stock would pass through is measured
- **WHEN** the drawn hobbed bolt and the drawn idler bearing are compared
- **THEN** they share metal where the stock would run between them, which is
  the design drawing the idler shut on nothing

#### Scenario: The hot end's axis is compared with the channel's
- **WHEN** the axis the hot end is drawn on and the axis the extruder cuts
  its filament channel on are compared
- **THEN** they differ by the offset the design's own extruder slice applies
  to every nozzle-holder feature it cuts

#### Scenario: The room at the mouth itself is measured
- **WHEN** the face of the extruder handle's plate and the axis of the channel
  it stands beside are compared
- **THEN** the plate stands nearer that axis than a stock radius, so a strand
  drawn on the axis touches it; and where the run goes in it is that overhang
  that puts it into the plate, and nowhere over the plate does the run pass
  through it rather than graze it

### Requirement: The filament travels to the viewer as a shape
The strand SHALL be published to viewers as its parametric shape with an
expression for each of its parameters, as the belts and the springs are,
rather than as a mesh per position, so that a viewer redraws the run itself
as the machine moves.

#### Scenario: The document is serialized
- **WHEN** the machine is serialized
- **THEN** the filament appears as a flexible shape whose parameters are the
  two places its free run is pinned, those parameters name the drivers that
  move the print head, and no filament appears as a mesh reference
