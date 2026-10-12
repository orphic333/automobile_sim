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
- **Wiebe function** — a curve describing how much of the fuel's energy has burned so far, as a fraction (0 to 1), as a function of crank angle since ignition. Used in `piston.py` (`_wiebe_fraction`) so combustion is spread over a ~40° burn window instead of releasing all its heat in one instant at TDC — this is also why peak cylinder pressure now lands a little after TDC rather than exactly on it, matching how real engines actually burn.
- **Isentropic compression / expansion** — compressing or expanding a gas with no heat lost to the surroundings. An idealization, but a reasonable one for how fast combustion happens.
- **AFR (Air-Fuel Ratio)** — the mass ratio of air to fuel burned. 14.7:1 is the stoichiometric ("exactly enough air") ratio for gasoline.
- **LHV (Lower Heating Value)** — how much energy is released burning a kilogram of fuel.

## A Full Cycle (I4 Reference)

This walks through what one cylinder does over its entire 720° cycle, then how four cylinders sharing one crankshaft (an I4) fit together. Bolded terms are defined above.

**One cylinder, 720°.** A 4-stroke engine needs two full crankshaft rotations (720°) to complete one cycle, because each physical stroke — up or down — gets 180°:

1. **Intake (0–180° of this stage, local angle 360–540° in the code):** the piston moves down from **TDC** toward **BDC**, pulling in a fresh **AFR**-mixed charge of air and fuel. How much actually gets trapped is the **VE**, further restricted by how open the **throttle** is. *Not yet modeled in `piston.py` — still a listed simplification, so this stroke currently costs and produces nothing.*
2. **Compression (local angle 540–720°):** the piston moves back up from BDC to TDC, squeezing the trapped charge. This is **isentropic compression** — no heat added, pressure and temperature rise purely from the **compression ratio**. The gas pushes back against the piston the whole way, which is real resistance the crankshaft has to spend **torque** overcoming — this is what `_compression_state` in `piston.py` computes.
3. **Power / combustion + expansion (local angle 0–180°):** at TDC, ignition starts. Instead of releasing all the fuel's energy at once, the **Wiebe function** spreads it over a ~40° burn window while the piston is already moving — that's why peak pressure lands a bit after TDC rather than exactly on it. Once the burn finishes, the hot, high-pressure gas keeps pushing the piston down through pure **isentropic** expansion. This stroke is where essentially all of a cylinder's positive torque comes from.
4. **Exhaust (local angle 180–360°):** the piston moves back up, pushing the spent gas out. *Also not yet modeled — another still-open simplification.*

Averaged over the whole 720°, the real, constantly-changing pressure this cycle produces is what **MEP** summarizes as one number — **IMEP** if you compute it straight from the thermodynamics, **BMEP** once friction and pumping losses are subtracted.

**Four cylinders, one crankshaft (I4).** `crankshaft.py`'s `CONFIGS["inline"]["I4"]` offsets the four cylinders by `(0, 180, 360, 540)` degrees. Each cylinder runs the exact same 720° cycle above, just starting at a different point in it — so at any instant, all four strokes are happening at once, one per cylinder:

| Global crank angle | Cylinder 1 (offset 0) | Cylinder 2 (offset 180) | Cylinder 3 (offset 360) | Cylinder 4 (offset 540) |
|---|---|---|---|---|
| 0° | Power (ignition) | Exhaust | Intake | Compression (near TDC) |

That's the whole reason multiple cylinders exist: one cylinder's power stroke only covers a quarter of the full cycle, so by staggering four of them evenly, there's always one currently producing torque — smoothing out what would otherwise be a very lumpy, stop-start push. Each cylinder's contribution still has to pass through the **leverage factor** (how well the **crank radius** and **connecting rod length** convert that piston push into actual twist) before it's summed into the crankshaft's net **torque** for that instant.

## Crankshaft & Motion

- **Torque** — twisting force. What actually turns the crankshaft.
- **Load torque** — resistance fighting the engine's rotation (friction, drag, whatever it's turning). Torque produced minus load torque is what accelerates (or slows) the engine.
- **Inertia** — resistance to a change in rotational speed. A heavier flywheel means the same torque produces less acceleration — revs change more sluggishly.
- **Equilibrium RPM** — the speed where torque produced equals torque demanded by the load. The engine naturally settles here and stops climbing.
- **Timestep / substep** — advancing the simulation by a small slice of time, assuming things stay constant for that slice. Smaller slices track fast-changing values (like torque) more accurately.
