## 1. Dimensions the strand needs

- [x] 1.1 Probe `diameter` from `FilamentSpoolHolder.scad` in `params.py` as the stock this machine is loaded with, and note that the file declares it and uses it nowhere
- [x] 1.2 Restate the filament channel `extruder_slice()` cuts (`translate([-1.9,0]) square([3.2,70])` and the slice height `H`) in the module-body block at the foot of `params.py`, annotated with the module it belongs to and with the fact that the cut's 70 is an over-run past the profile rather than a height
- [x] 1.3 Restate the reel's own dimensions there too — `FilamentSpool()` writes them as bare numbers inside its module — so the strand and the tube read one source

## 2. What filament is here

- [x] 2.1 Write `metamaquina2/filament.py`: the layer's radius, pitch and turn count derived from the reel and the stock, and the frame the strand's own path is authored in
- [x] 2.2 Add the `Filament(MolejoNode)` leaf: ABS colour, `TranslationalPort`s for the two places the free run is pinned, the design's .scad source set in its own file set, and a `render()` returning a `Circle` section swept along one `Helix` continued by one `Spline`
- [x] 2.3 Declare the sweep's tessellation per turn rather than per strand, as the springs do, and record what it costs the free run that molejo spends the same budget on every element of a path
- [x] 2.4 Record on the module why the coil is one layer and not a reel, why the run leaves the reel at whole turns, and how a machine point is read in the strand's own frame
- [x] 2.5 Record that the layer lies on the tube with no gap, so the chords between its rings share three tenths of a millimetre with it everywhere: the alternative is a clearance between a reel and the filament on it, or a tessellation deciding a diameter

## 3. The reel under the layer

- [x] 3.1 Draw `FilamentSpool`'s tube to what is wound under the outermost layer, derived from the design's own reel diameter and the stock, and record there that the layer is drawn as the strand it is

## 4. Where the machine takes the filament in

- [x] 4.1 Publish `FILAMENT_ENTRY` in `extruder.py`: where the channel opens, in the extruder's own frame
- [x] 4.2 Publish the same point in the carriage's frame in `x_carriage.py`, from the placement the carriage already makes, and name that placement rather than writing it twice
- [x] 4.3 Publish `filament_entry(position)` in `x_stage.py`: the same point in the beam's frame, as a function of where the carriage is, the way `x_belt.pulley_angle` is
- [x] 4.4 Publish the height the spool holder stands its reel at, so the machine can place the strand from it

## 5. The strand on the machine

- [x] 5.1 Place `Filament` on the root beside the spool holder, turned so its coil axis runs down the reel's and its exit leaves the top of it towards the machine
- [x] 5.2 Bind the ports in `Metamaquina2.render()` from the entry point the beam publishes, plus the machine's own lift, read into the strand's frame
- [x] 5.3 Carry the run over the machine rather than through it: derive the crossing from the frame's own height and width, since a run drawn straight from the reel to the extruder passes through the right-hand side panel, the beam's plate and the box at the beam's end
- [x] 5.4 Record where the run ends and why it ends there: the handle plate overhanging the channel at the mouth, the pinch the design draws shut, the 0.3 the hot end and the channel disagree by, and the liner bore that is the size of the stock

## 6. The contracts

- [x] 6.1 Red first: assert the machine carries a filament that is a flexible molejo leaf with its own ports, before it does
- [x] 6.2 Assert the wound layer runs at one radius about the reel's axis, reaches the design's own reel diameter, and lies within the reel's width
- [x] 6.3 Assert the layer rests on the reel tube — reaching the surface it is drawn to and standing no further out than the drawing's own section resolves — and that the tube is one stock diameter smaller on the radius than the design's reel
- [x] 6.4 Assert consecutive turns are one stock diameter apart, that the layer takes up no more of the reel than it has, and that one more turn would not fit
- [x] 6.5 Assert the run ends at the mouth of the extruder's filament channel, on the axis the design cuts it on, and arrives along it rather than across it
- [x] 6.6 Assert the run shares metal with no part of the frame or the beam, at rest and at both ends of both travels
- [x] 6.7 Assert driving X moves the end of the run with the extruder, redraws the run between its crossing and its end, and leaves the crossing and the turns on the reel where they were; assert the same for Z
- [x] 6.8 Assert the strand is watertight, in one piece and of positive volume, at rest and at both ends of the X and Z travel
- [x] 6.9 Assert the four things that stop the run at the mouth: the handle plate's overhang and the graze it makes, the hobbed bolt and the idler bearing sharing metal, the hot end's axis against the channel's, and the liner bore against the stock
- [x] 6.10 Assert the machine's serialized document publishes the filament as a flexible shape with one expression per parameter, naming the drivers that move the head

## 7. Record and close

- [x] 7.1 Update the `metamaquina2.py` module docstring with what the filament is, how it crosses the machine, and where it stops
- [x] 7.2 Run the whole suite green and confirm the previously passing 56 contracts still pass
- [x] 7.3 Mutation check: break the layer's radius, the turn count, the entry binding, the frame the entry is read in, and the height the run crosses at; confirm the contracts that own each go red, revert, confirm green
- [x] 7.4 Build the machine and take snapshots of it loaded, and look at them: pixels are evidence for CAD work
- [x] 7.5 Sync `openspec/specs/filament-path/` and archive the change
