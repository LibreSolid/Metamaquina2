# OpenSCAD Design Reading Specification

## Purpose

Keep the decade-old OpenSCAD design the single source of truth while the
solid-node layer reads it: geometry comes from the design's own modules,
dimensions from the design's own variables, and an edit to either reaches
every part that depends on it.

## Requirements

### Requirement: Leaf geometry comes from the design's own OpenSCAD modules
The wrapper SHALL NOT restate or replace the OpenSCAD sources. Every leaf
whose part the design draws SHALL render the design's own module, reached
through a `use`-style import of the absolute source path so the design's
internal `include`/`use` chains keep resolving from the source directory.
Parts the wrapper draws itself SHALL state the design's own curve
resolution rather than inherit OpenSCAD's coarser defaults.

#### Scenario: A leaf renders a design module
- **WHEN** a leaf node such as a panel, bolt, or bearing is built
- **THEN** its geometry is the OpenSCAD module the design defines for that
  part, evaluated in the source directory, and the .scad sources are
  unmodified

#### Scenario: A wrapper-drawn curve matches the design's resolution
- **WHEN** the wrapper draws a curved primitive of its own
- **THEN** the primitive carries the design's facet settings, so an 8 mm
  rod is not coarser than the same rod drawn by a design module

### Requirement: Dimensions are probed from the OpenSCAD sources at import
Every dimension the wrapper places parts with SHALL be evaluated by
OpenSCAD itself from the design's sources at package import, not restated
in Python. Probed scalars SHALL be recovered beyond OpenSCAD's six-digit
echo precision so parts that must meet flush do. A probed name the source
does not define SHALL fail the import with an error naming it. A value the
design writes down only inside a module body, where a probe cannot reach,
MAY be restated in Python, and SHALL be annotated with the module it
belongs to.

#### Scenario: A design dimension reaches the wrapper
- **WHEN** the package imports
- **THEN** names such as `BuildVolume_X`, `machine_height`, and
  `XCarPosition` hold the values the design's own variable chain
  evaluates to

#### Scenario: A probe asks for a name the design lost
- **WHEN** a probed variable is renamed or removed from the .scad sources
- **THEN** importing the package raises an error naming the missing
  variable and its source file

### Requirement: Editing any OpenSCAD source invalidates every part
Because the framework's dependency walk sees Python imports only, every
part node SHALL include the design's whole .scad and .h source set in its
own file set, so an edit to any source file rebuilds the parts rather than
serving stale geometry.

#### Scenario: A design file is edited
- **WHEN** any .scad or .h file in the source directory changes
- **THEN** every part reports itself out of date and rebuilds

### Requirement: Sheet parts are authored as the profile that gets cut
A part cut from flat stock SHALL be authored as its 2D profile; the
extrusion to the stock thickness SHALL follow from the part's declared
sheet thickness so profile and thickness cannot be written down
inconsistently.

#### Scenario: A sheet part renders
- **WHEN** a sheet part is built
- **THEN** its geometry is its declared 2D profile extruded by its
  declared stock thickness
