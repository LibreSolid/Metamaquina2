## ADDED Requirements

### Requirement: The reel carries its outermost layer as drawn stock
The reel SHALL be drawn as two things rather than one: the wound tube the
design draws, and its outermost layer, drawn as a single strand of the stock
diameter the design names. The tube SHALL be what is wound under that layer,
so that the two together reach the reel's own outside diameter exactly. The
strand SHALL lie on the tube, touching it and cutting into nothing.

#### Scenario: The loaded stand is looked at from the end
- **WHEN** the assembly is built
- **THEN** the strand lying on the reel runs at one radius about the reel's
  own axis, and its outside reaches the design's reel diameter

#### Scenario: The layer is measured against the tube it lies on
- **WHEN** the strand and the reel tube are compared
- **THEN** the strand rests on the tube without sharing metal with it, and
  the tube is one stock diameter smaller on the radius than the design's reel

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

### Requirement: The free run follows the print head
The strand SHALL be a flexible leaf: where the run ends SHALL arrive through
declared ports, and the machine SHALL bind them from where it puts its own
extruder rather than from a position written down a second time. Driving the
machine SHALL redraw the run and SHALL leave the wound layer where it lies,
because a reel does not turn when a print head moves.

#### Scenario: The carriage is driven along the beam
- **WHEN** the X driver is displaced
- **THEN** the end of the run moves with the extruder by that displacement,
  the strand is a different shape, and the turns lying on the reel have not
  moved

#### Scenario: The beam is driven up its screws
- **WHEN** the Z driver is displaced
- **THEN** the end of the run rises with the extruder, the strand is a
  different shape, and the turns lying on the reel have not moved

### Requirement: The strand is one continuous piece of stock
The strand SHALL come out of its evaluator as a single closed body,
watertight and in one piece, at every position the machine's drivers can
reach.

#### Scenario: The strand is swept
- **WHEN** the strand's mesh is inspected, at rest and across the travel
- **THEN** it is watertight, in one piece, and of positive volume

### Requirement: The run ends where the drawn machine stops leaving room for it
The run SHALL be drawn only as far as the channel's mouth. Where the drawn
machine leaves no room for stock below that mouth, each such place SHALL be
recorded where the run ends and asked for by contract, so that a later change
to the design or to the hot end cannot make one of them quietly go away.

#### Scenario: The pinch the stock would pass through is measured
- **WHEN** the drawn hobbed bolt and the drawn idler bearing are compared
- **THEN** they share metal where the stock would run between them, which is
  the design drawing the idler shut on nothing

#### Scenario: The hot end's axis is compared with the channel's
- **WHEN** the axis the hot end is drawn on and the axis the extruder cuts
  its filament channel on are compared
- **THEN** they differ by the offset the design's own extruder slice applies
  to every nozzle-holder feature it cuts

### Requirement: The filament travels to the viewer as a shape
The strand SHALL be published to viewers as its parametric shape with an
expression for each of its parameters, as the belts and the springs are,
rather than as a mesh per position, so that a viewer redraws the run itself
as the machine moves.

#### Scenario: The document is serialized
- **WHEN** the machine is serialized
- **THEN** the filament appears as a flexible shape whose parameters are the
  place the run ends, and no filament appears as a mesh reference
