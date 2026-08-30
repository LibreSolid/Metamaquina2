# Z Screw Drive Specification

## Purpose

Hang the X stage on the thread its nuts really climb: exact M8 screws
that the beam's weight comes down on, nuts cut from the same thread
authority, and a lift that is what the screws' angle is worth rather
than a height somebody typed in.

## Requirements

### Requirement: The threaded bars are exact thread, drawn from one authority
Every M8 bar -- the two Z bars and the four horizontal frame bars --
SHALL be drawn as the ISO metric basic profile swept up a helix at one
pitch per turn, as an exact boundary-kernel solid rather than a
tessellation, because the working clearance is finer than a mesh
tolerance. Each nut SHALL be cut by the same profile grown by one
recorded clearance, so bar and nut cannot be given two different thread
forms by accident.

#### Scenario: A nut and its bar are asked as solids
- **WHEN** a Z nut and its bar are compared as exact solids at any height
- **THEN** they share no volume, and the nut's nearest approach to the
  bar is the recorded clearance -- meshed, not merely clear

### Requirement: The beam hangs on its nuts
Each X end SHALL carry the M8 nut its Z link captures, seated with its
top face against the link's plate, and the beam's height SHALL be
exactly what the screws' angle is worth through the thread's lead. The
bars SHALL be turned by the one constant phase that lines their thread
up with the nuts' -- the turn a builder puts in once with the screws in
their hands -- so nut and bar stay threaded at every height of the
travel, not only at heights that fall on a whole pitch.

#### Scenario: The travel is swept
- **WHEN** the beam is placed at many heights across the declared travel,
  including heights that are not a whole number of leads
- **THEN** both nuts remain threaded on their bars with no interference
  anywhere

### Requirement: What is clamped to a turning shaft turns with it
The couplings joining the Z bars to their motor shafts SHALL turn with
the bars, by the same angle the driver holds.

#### Scenario: Z is driven
- **WHEN** the Z driver changes
- **THEN** the bars and their couplings have turned by the driven angle
  while the motors' bodies stand still
