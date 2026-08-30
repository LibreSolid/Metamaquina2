## MODIFIED Requirements

### Requirement: The free run gets over the machine rather than through it
The stand is beside the machine and the extruder is inside it, so the free run
SHALL be carried over the machine clear of everything that stands in its way,
and SHALL come down into the channel through the opening the frame leaves for
the carriage to travel in. What stands in its way SHALL include the print head
itself, which at the top of its travel is lifted above every sheet the frame
carries. It SHALL share metal with no part of the frame or of the beam, at any
position the machine's drivers can reach.

#### Scenario: The run is measured against the machine it crosses
- **WHEN** the strand and the parts of the frame and the beam are compared, at
  rest and at each of the four corners of the two travels the print head moves
  along
- **THEN** the run shares metal with none of them

#### Scenario: The head is compared with the frame at the top of its travel
- **WHEN** the beam is driven to the top of its declared travel, and the
  highest the head reaches, the highest the frame reaches and the height the
  run crosses at are compared
- **THEN** the head stands above the frame, so what the run has to clear there
  is the head and not the frame; and the run crosses above the head
