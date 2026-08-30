## 1. Dimensions the hot end needs

- [ ] 1.1 Probe `jhead_length`, `jhead_instalation_depth` and `inch` from `Metamaquina2.scad` in `params.py`
- [ ] 1.2 Restate the holder's ⌀10.4 groove root (`r1` in `J_head_body()`, `jhead.scad`) in the module-body block at the foot of `params.py`, annotated with the module it belongs to and with the fact that OpenSCAD cannot parse the file it is in
- [ ] 1.3 Restate the PTFE liner's outline (`PTFE_liner_2d_outline()` in `PTFE_liner.scad`) and the two M3x30 hole positions (`extruder_slice()` in `lasercut_extruder.scad`) in the same block
- [ ] 1.4 Import `nozzle.scad` in `scad.py`
- [ ] 1.5 Add the PTFE and ceramic colours to `materials.py`, with the note that the design's palette never had to name them

## 2. What a J-head is

- [ ] 2.1 Write `metamaquina2/jhead.py`: the two shop drawings' own numbers for the holder and for the nozzle, each named for the drawing it comes off
- [ ] 2.2 Derive the holder's body length from `jhead_length`, `jhead_instalation_depth`, the holder's own shoulder and the nozzle's own reach below its block, and record there why the length is the free number and the others are not
- [ ] 2.3 Derive the filament bore from the ⌀10.4 groove root and the drawing's minimum groove wall, and record that only the thin end of the drawing's wall range leaves a bore the design's own liner passes down
- [ ] 2.4 Derive where the nozzle's threaded stub tops out, which is what the liner is drawn to
- [ ] 2.5 Publish the slip fit a part pressed into a drilled hole is drawn with, and the argument for drawing one rather than a coincident surface
- [ ] 2.6 Record in the module docstring that `jhead.scad` is unparseable, what its conflict is over, and why the holder is drawn here instead of the file being repaired

## 3. The five parts

- [ ] 3.1 `NozzleHolder(ScadPart)`: collar, neck, 5/8" body and shoulder about the mount plane, five grooves milled over the drawing's three sectors, and the three bores -- the 5/16-24 tap drill at the top, the filament bore, and the 3/8-24 tap drill up from the foot to meet it
- [ ] 3.2 `PTFELiner(ScadPart)`: the design's own outline, rotate-extruded, at the length the holder and the nozzle leave it, with the disagreement with `PTFE_liner.scad`'s own 47 mm recorded on the class
- [ ] 3.3 `Nozzle(ScadPart)`: the design's `v4nozzle()`, and a note that its stub is drawn 5/16 where its own drawing says 3/8
- [ ] 3.4 `HeaterResistor(ScadPart)` and `Thermistor(ScadPart)`: a body the size of the hole the nozzle module drills for it, and leads at a nominal gauge, both recorded as such
- [ ] 3.5 `HotEnd(AssemblyNode)`: the five of them stacked about the filament axis, on the mount plane, turned so the block faces the way the design's own call faces

## 4. Where it hangs

- [ ] 4.1 `Extruder` carries the hot end at its own origin, counter-rotated so the design's world orientation is kept, and the two M3x30 in the holes `extruder_slice()` cuts for them
- [ ] 4.2 `XCarriage` loses the paragraph that explained why there was no hot end

## 5. The contracts

- [ ] 5.1 Red first: assert the extruder carries a hot end of the five bought parts and two M3x30, before any of them exist
- [ ] 5.2 Assert the nozzle tip stands `jhead_length - jhead_instalation_depth` below the holder's shoulder, and that the shoulder stands on the extruder's underside
- [ ] 5.3 Assert `HomeZ` brings the nozzle tip down onto the build surface, touching the glass and cutting into it no more than two touching surfaces leave
- [ ] 5.4 Assert the stack: nozzle block against holder shoulder, liner from the holder's top face to the nozzle's stub, and no pair of hot end parts sharing metal
- [ ] 5.5 Assert the liner runs the bore with the clearance the derivation leaves, and that it is shorter than `PTFE_liner.scad`'s 47 mm by exactly the room the stack takes
- [ ] 5.6 Assert the resistor and the thermistor each stand in the hole the nozzle module drills for them, clear of the brass, and reach out of the block
- [ ] 5.7 Assert the hot end travels with the carriage when X is driven and with the beam when Z is driven

## 6. Record and close

- [ ] 6.1 Update the `metamaquina2.py` module docstring with what the hot end is and where its two derived numbers come from
- [ ] 6.2 Run the whole suite green and confirm the previously passing contracts still pass
- [ ] 6.3 Take a snapshot of the hot end and of the carriage and look at them: pixels are evidence for CAD work
- [ ] 6.4 Sync `openspec/specs/hot-end/` and archive the change
