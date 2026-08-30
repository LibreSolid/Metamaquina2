# Assembly Tree Specification

## Purpose

Read the machine as a buildable assembly: a tree whose leaves are the
parts a builder handles and whose assemblies are the groups that go
together before they go into something bigger, with the placements this
layer is responsible for held as contracts.

## Requirements

### Requirement: The machine is a solid-node model with a declared entry point
The project SHALL declare `metamaquina2.metamaquina2:Metamaquina2` as its
solid-node model in `pyproject.toml`, so the solid CLI and the studio open
the whole machine from the repository root without further configuration.

#### Scenario: The studio opens the project
- **WHEN** the project is opened by a solid-node host
- **THEN** the mounted model is the complete Metamaquina 2 assembly tree

### Requirement: The tree follows the build, not the source file
Every part a builder handles SHALL be a leaf; every group that is
assembled before it goes into something bigger SHALL be an assembly node.
The root SHALL assemble the frame, the Z axis, the Y axis, the X stage,
and the electronics, with the spool holder as a separate stand beside the
machine where the design draws it.

#### Scenario: A builder walks the tree
- **WHEN** the assembly tree is inspected
- **THEN** each subassembly matches a stage of the physical build and
  each leaf is one handled part -- a plate that gets cut, a bolt that
  gets turned, a bearing that gets pressed

### Requirement: Moving parts stand on the parts that carry them
At the rest pose and across each axis's declared travel, the placements
this layer is responsible for SHALL hold: every X carriage bearing on an
X rod, all three Y platform bearings on a Y rod, both X ends hung on the
Z rods, and the build-surface glass resting on the heated bed rather than
above it.

#### Scenario: The carriage rides its rods
- **WHEN** the assembly is built at the rest pose or at either end of the
  X travel
- **THEN** every carriage bearing is coaxial with an X rod

#### Scenario: The bed rests on its parts
- **WHEN** the assembly is built
- **THEN** the glass sits on the heated bed and the three platform
  bearings are on the Y rods

#### Scenario: The beam hangs on the Z rods
- **WHEN** the assembly is built anywhere across the Z travel
- **THEN** both X ends remain on the Z rods

### Requirement: The machine advertises the build volume it reaches
The heated bed SHALL cover the advertised build area, and the declared
driver travels SHALL span the advertised build volume: X and Y half of it
either side of centre, Z the full height from the build surface up.

#### Scenario: The bed covers the build area
- **WHEN** the bed and the advertised build volume are compared
- **THEN** the bed is at least as wide and deep as the build area
