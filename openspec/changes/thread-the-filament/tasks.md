## 1. Dimensions the strand needs

- [ ] 1.1 Probe `diameter` from `FilamentSpoolHolder.scad` in `params.py` as the stock this machine is loaded with, and note that the file declares it and uses it nowhere
- [ ] 1.2 Restate the filament channel `extruder_slice()` cuts (`translate([-1.9,0]) square([3.2,70])` and the slice height `H`) in the module-body block at the foot of `params.py`, annotated with the module it belongs to and with the fact that the cut's 70 is an over-run past the profile rather than a height

## 2. What filament is here

- [ ] 2.1 Write `metamaquina2/filament.py`: the layer's radius, pitch and turn count derived from the reel and the stock, and the frame the strand's own path is authored in
- [ ] 2.2 Add the `Filament(MolejoNode)` leaf: ABS colour, three `TranslationalPort`s for where the run ends, the design's .scad source set in its own file set, and a `render()` returning a `Circle` section swept along one `Helix` continued by one `Spline`
- [ ] 2.3 Declare the sweep's tessellation per turn rather than per strand, as the springs do, and record what it costs the free run that molejo spends the same budget on every element of a path
- [ ] 2.4 Record on the module why the coil is one layer and not a reel, why the run leaves the reel at whole turns, and how a machine point is read in the strand's own frame

## 3. The reel under the layer

- [ ] 3.1 Draw `FilamentSpool`'s tube to what is wound under the outermost layer, derived from the design's own reel diameter and the stock, and record there that the layer is drawn as the strand it is

## 4. Where the machine takes the filament in

- [ ] 4.1 Publish `FILAMENT_ENTRY` in `extruder.py`: where the channel opens, in the extruder's own frame
- [ ] 4.2 Publish the same point in the carriage's frame in `x_carriage.py`, from the placement the carriage already makes, and name that placement rather than writing it twice
- [ ] 4.3 Publish `filament_entry(position)` in `x_stage.py`: the same point in the beam's frame, as a function of where the carriage is, the way `x_belt.pulley_angle` is
- [ ] 4.4 Publish the height the spool holder stands its reel at, so the machine can place the strand from it

## 5. The strand on the machine

- [ ] 5.1 Place `Filament` on the root beside the spool holder, turned so its coil axis runs down the reel's and its exit leaves the top of it towards the machine
- [ ] 5.2 Bind the three ports in `Metamaquina2.render()` from the entry point the beam publishes, plus the machine's own lift, read into the strand's frame
- [ ] 5.3 Record where the run ends and why it ends there: the pinch the design draws shut, the 0.3 the hot end and the channel disagree by, and the liner bore that is the size of the stock

## 6. The contracts

- [ ] 6.1 Red first: assert the machine carries a filament that is a flexible molejo leaf with three ports, before it does
- [ ] 6.2 Assert the wound layer runs at one radius about the reel's axis, reaches the design's own reel diameter, and lies within the reel's width
- [ ] 6.3 Assert the layer rests on the reel tube without cutting into it, and that the tube is one stock diameter smaller on the radius than the design's reel
- [ ] 6.4 Assert consecutive turns are one stock diameter apart and that one more turn would not fit across the reel
- [ ] 6.5 Assert the run ends at the mouth of the extruder's filament channel, on the axis the design cuts it on, and arrives along it rather than across it
- [ ] 6.6 Assert driving X moves the end of the run with the extruder, changes the strand's shape, and leaves the turns on the reel where they were; assert the same for Z
- [ ] 6.7 Assert the strand is watertight, in one piece and of positive volume, at rest and at both ends of the X and Z travel
- [ ] 6.8 Assert the hobbed bolt and the idler bearing share metal where the stock would pass between them, and that the hot end's axis and the channel's differ by the design's own offset
- [ ] 6.9 Assert the machine's serialized document publishes the filament as a flexible shape with one expression per parameter

## 7. Record and close

- [ ] 7.1 Update the `metamaquina2.py` module docstring with what the filament is and where it stops
- [ ] 7.2 Run the whole suite green and confirm the previously passing 56 contracts still pass
- [ ] 7.3 Mutation check: break the layer's radius and the entry binding in node code, confirm the contracts that own them go red, revert, confirm green
- [ ] 7.4 Build the machine and take snapshots of the stand, of the run and of the extruder, and look at them: pixels are evidence for CAD work
- [ ] 7.5 Sync `openspec/specs/filament-path/` and archive the change
