## 1. Red first

- [x] 1.1 Ask the routing contract at the four corners of the two travels rather than at each axis' ends with the other at rest, and watch it fail on the frame's right-hand side panel, its top panel and the right-hand rod-end plates
- [x] 1.2 Add the contract that records the finding: with the beam at the top of its travel the print head stands above every sheet the frame carries, and the run crosses above the head by the clearance the machine declares

## 2. How high the machine's head stands

- [x] 2.1 `HandleHeight` is already probed in `params.py`, beside the `HandleWidth` the design declares it with, and nothing had needed it
- [x] 2.2 Publish in `handle.py` how high the handle's plate stands in the extruder's frame
- [x] 2.3 Publish in `extruder.py` that this is the highest the extruder stands, and in `x_carriage.py` and `x_stage.py` the same height in their own frames, the way the filament entry already travels

## 3. Where the run crosses

- [x] 3.1 Move `CROSSING_X` and `CROSSING_Z` from `filament.py` to `metamaquina2.py`, since what they are made of is the beam and the travel
- [x] 3.2 Derive the crossing height from the highest the head reaches at the top of the declared Z travel, plus a stated clearance, and record why the frame's own top is not what it is measured from
- [x] 3.3 Turn the run down over the extruder rather than curving it straight at the channel, so the route does not depend on how a spline sags, and record what that costs: a third span, drawn at the same tessellation as the whole wound layer
- [x] 3.4 Correct the sentence in `filament.py` that says there is nothing above the crossing, and say instead what the run has to get over

## 4. The contracts that had to move with it

- [x] 4.1 Ask "redrawn rather than carried" as the run's own length rather than as a point partway along it: X lengthens the level stretch and Z lengthens the drop, so no one point proves both

## 5. The record

- [x] 5.1 Update the machine's module docstring: the run gets over the head, not only over the frame
- [x] 5.2 Mutation-check the new contracts, run the suite, build, and look at the machine at the corners of the travel
