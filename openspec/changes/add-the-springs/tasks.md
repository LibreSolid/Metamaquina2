## 1. Dimensions the springs need

- [ ] 1.1 Probe `heatedbed_spring_length`, `heatedbed_spring_compressed_length`, `m4_diameter`, `m4_washer_thickness` and `m3_washer_D` from `Metamaquina2.scad` in `params.py`
- [ ] 1.2 Restate the heated bed's mounting-hole inset (`border = 5` in `heated_bed_pcb_curves()`, `heated_bed.scad`) in the module-body block at the foot of `params.py`, annotated with the module it belongs to

## 2. What a compression spring is

- [ ] 2.1 Write `metamaquina2/spring.py`: `wire()` deriving wire thickness from the catalogue diameter, the shank bore and a declared bore clearance; `turns()` deriving the coil count from an installed length and that wire
- [ ] 2.2 Add the `Spring(MolejoNode)` base: metal colour, a `height` `TranslationalPort`, the design's .scad source set in its own file set, and a `render()` returning a `Circle` section swept along one `Helix` at `P.height`
- [ ] 2.3 Declare the sweep's tessellation per turn rather than per spring, so a six-turn and a ten-turn spring are drawn to the same fineness
- [ ] 2.4 Record on the class that the helix's own length is one wire diameter short of the space the spring occupies, and that the end coils are neither closed nor ground

## 3. The four bed levelling springs

- [ ] 3.1 Add `BedSpring(Spring)` with the CM351 line's diameter and free length and the M3 shank it is threaded on
- [ ] 3.2 Derive in the same module the gap the platform deck and the bed board leave, from `pcb_height`, `YPlatform_zoffset` and `thickness`, and record there the design's disagreeing `heatedbed_spring_compressed_length` and where the 0.3 mm comes from
- [ ] 3.3 Add `BedLevelScrew(AssemblyNode)` on the platform deck's top face: the M3x30 head-down through the bed, a washer under its head, a washer under the board seating the spring, the spring, a washer under the platform and the nut under that; `render()` connects the spring's `height`
- [ ] 3.4 Place four of them in `YPlatform` at the corner holes derived from `heated_bed_pcb_width`, `heated_bed_pcb_height` and the hole inset
- [ ] 3.5 Record in `BedLevelScrew` that the bill of materials buys a wing nut the design draws no module for, and that the plain hex nut stands in for it

## 4. The two idler springs

- [ ] 4.1 Publish the handle's placement as `POSITION` in `handle.py` and read it from `extruder.py`
- [ ] 4.2 Publish `back_face` on `Idler`: where the back plate's outer face stands in the extruder's flat frame, a radius out from the pivot
- [ ] 4.3 Add `IdlerSpring(Spring)` with the CM1678 line's diameter and free length and the M4 shank it is threaded on
- [ ] 4.4 Seat a washer and a spring on each handle bolt at the back plate's outer face, derived from `POSITION` and `Idler.back_face`; `Handle.render()` connects each spring's `height` to its free length, and records the bare shank the design leaves for the preload nut it never draws

## 5. The contracts

- [ ] 5.1 Red first: assert four bed springs and two idler springs exist as flexible molejo leaves with exactly one port each, before any of them do
- [ ] 5.2 Assert each bed spring stands on the platform sheet and reaches the washer under the bed board, touching both and cutting into neither
- [ ] 5.3 Assert the bed springs travel with the bed when Y is driven, and that nothing else does
- [ ] 5.4 Assert each idler spring is seated on the idler back plate's outer face and cuts into neither the plate nor the bolt
- [ ] 5.5 Assert every spring's bolt passes through its coil at the declared clearance without touching it
- [ ] 5.6 Assert every spring's coils clear each other by at least a wire diameter at its bound length, and that the bound length is inside the free length the bill of materials buys
- [ ] 5.7 Assert every spring's mesh is watertight, in one piece and of positive volume
- [ ] 5.8 Assert the machine's serialized document publishes six springs as flexible shapes with one parameter each
- [ ] 5.9 Assert the bed's installed spring length differs from `heatedbed_spring_compressed_length` by exactly the design's own two statements of the deck height

## 6. Record and close

- [ ] 6.1 Update the `metamaquina2.py` module docstring with what the springs are and why they are drawn to the gap
- [ ] 6.2 Run the whole suite green and confirm the previously passing 38 contracts still pass
- [ ] 6.3 Take a snapshot of the bed corner and of the extruder and look at them: pixels are evidence for CAD work
- [ ] 6.4 Sync `openspec/specs/spring-loading/` and archive the change
