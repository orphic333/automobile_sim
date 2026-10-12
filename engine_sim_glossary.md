# Engine Sim Glossary

Plain-language reference for terms used in `piston.py` and `crankshaft.py`. One line each — look things up as you need them, not all at once.

## Geometry

- **Bore** — the cylinder's internal diameter (how wide it is).
- **Stroke** — the distance the piston travels from top to bottom.
- **TDC / BDC** — Top Dead Center / Bottom Dead Center. The piston's highest and lowest points.
- **Swept volume** — the volume the piston clears as it moves from TDC to BDC. This is "engine displacement" when you add up all cylinders.
- **Clearance volume** — the small volume left above the piston at TDC, even when fully compressed. Combustion starts here.
- **Compression ratio (CR)** — how many times smaller the clearance volume is than the full volume at BDC. A CR of 10 means the gas gets squeezed into 1/10th its original space before ignition.
- **Crank radius (r)** — half the stroke. How far the crank pin sits from the crankshaft's center.
- **Connecting rod length (l)** — the rod linking the piston to the crank pin.
- **Slider-crank** — the mechanism converting the piston's up-down motion into the crankshaft's rotation.
- **Leverage factor** — how effectively piston force converts to torque at a given crank angle. Zero at TDC/BDC, highest around 90°.

## Pressure & Combustion

- **MEP (Mean Effective Pressure)** — a single "average" pressure that, if it stayed constant for the whole stroke, would produce the same work as the real, constantly-changing pressure. A shortcut for comparing engines without needing the full pressure trace.
- **IMEP** — MEP calculated straight from the thermodynamics (indicated). The theoretical ceiling.
- **BMEP** — MEP actually delivered at the crankshaft (brake), after friction and pumping losses eat into IMEP. Always lower than IMEP.
- **VE (Volumetric Efficiency)** — what fraction of the cylinder's theoretical max air/fuel charge actually gets trapped inside. Never 100% in a real engine; varies with RPM and throttle.
- **Throttle** — how open the throttle plate is (0 to 1). Restricts how much air/fuel gets in, which is what actually controls how much power the engine makes.
- **Otto cycle** — the idealized four-stage model (compress → ignite → expand → exhaust) used to work out combustion pressure from first principles, instead of guessing a curve shape.
- **Isentropic compression / expansion** — compressing or expanding a gas with no heat lost to the surroundings. An idealization, but a reasonable one for how fast combustion happens.
- **AFR (Air-Fuel Ratio)** — the mass ratio of air to fuel burned. 14.7:1 is the stoichiometric ("exactly enough air") ratio for gasoline.
- **LHV (Lower Heating Value)** — how much energy is released burning a kilogram of fuel.

## Crankshaft & Motion

- **Torque** — twisting force. What actually turns the crankshaft.
- **Load torque** — resistance fighting the engine's rotation (friction, drag, whatever it's turning). Torque produced minus load torque is what accelerates (or slows) the engine.
- **Inertia** — resistance to a change in rotational speed. A heavier flywheel means the same torque produces less acceleration — revs change more sluggishly.
- **Equilibrium RPM** — the speed where torque produced equals torque demanded by the load. The engine naturally settles here and stops climbing.
- **Timestep / substep** — advancing the simulation by a small slice of time, assuming things stay constant for that slice. Smaller slices track fast-changing values (like torque) more accurately.
