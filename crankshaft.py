import math

import numpy as np

from piston import Cylinder
# Firing offsets (degrees, over a 720-degree 4-stroke cycle) by engine
# family and layout. Pure data: the torque math below doesn't change
# per-layout, only which offsets it uses.
CONFIGS = {
    "inline": {
        "I2": (0, 360),
        "I3": (0, 240, 480),
        "I4": (0, 180, 360, 540),
        "I6": (0, 120, 240, 360, 480, 600),
    },
    "boxer": {
        "F4": (0, 180, 360, 540),
        "F6": (0, 120, 240, 360, 480, 600),
    },
}

class Crankshaft:
    """Sums piston forces into net engine torque via slider-crank geometry,
    and can integrate that torque forward in time to get crank speed.

    Units: stroke and rod_length in millimeters, forces in N, torque in N*m,
    inertia in kg*m^2, omega in rad/s, theta in radians.
    """

    def __init__(self, stroke, rod_length, cylinders, family, layout,
                 inertia=0.15, start_rpm=800):
        """
        stroke:      piston stroke (mm)
        rod_length:  connecting rod length l (mm)
        cylinders:   list of Cylinder objects, in firing-order position
                     (e.g. cylinder 1, 2, 3, 4) -- matched up with the
                     offsets for `family`/`layout`
        family:      key into CONFIGS, e.g. "inline", "boxer"
        layout:      key into CONFIGS[family], e.g. "I4", "F4"
        inertia:     flywheel + rotating-assembly moment of inertia (kg*m^2)
        start_rpm:   initial crank speed for step()
        """
        if rod_length <= stroke / 2:
            raise ValueError("rod_length must be greater than the crank radius")

        try:
            offsets = CONFIGS[family][layout]
        except KeyError:
            raise ValueError(f"Unknown configuration: {family}/{layout}")
        if len(cylinders) != len(offsets):
            raise ValueError(
                f"{family}/{layout} needs {len(offsets)} cylinders, got {len(cylinders)}"
            )

        self.stroke_m = stroke /1000
        self.r_m = stroke / 2000          # crank radius
        self.l_m = rod_length/1000          # connecting rod length
        self.family = family
        self.layout = layout
        self.cylinders = list(zip(cylinders, offsets))

        # Time-step state
        self.inertia = inertia
        self.omega = start_rpm * 2 * math.pi / 60   # rad/s
        self.theta_rad = 0.0                            # rad

    def _leverage(self, theta_local_deg):
        """Slider-crank leverage factor: sin(theta + beta) / cos(beta),
        where sin(beta) = (r / l) * sin(theta) is the rod angle."""
        theta = math.radians(theta_local_deg)
        sin_beta = (self.r_m / self.l_m) * math.sin(theta)
        cos_beta = math.sqrt(1.0 - sin_beta ** 2)
        beta = math.asin(sin_beta)
        return math.sin(theta + beta) / cos_beta

    def calculate_net_torque(self, current_rpm, theta_global, throttle=1.0):
        """Net crankshaft torque (N*m) at the given RPM and global crank
        angle (0-720 degrees for a 4-stroke cycle)."""
        net_torque = 0.0

        for cylinder, offset in self.cylinders:
            # 1. Local angle within this cylinder's own 720-degree cycle
            theta_local = (theta_global - offset) % 720

            # 2. Piston force: the cylinder itself now decides which
            #    strokes produce force (power stroke pushes, compression
            #    stroke resists, intake/exhaust are still zero) and shapes
            #    it by where in that stroke the piston currently is
            f_p = cylinder.calculate_downward_force(current_rpm, theta_local, throttle)

            # 3. Torque = F_p * r * leverage
            net_torque += f_p * self.r_m * self._leverage(theta_local)

        return net_torque

    def step(self, dt, load_torque=0.0, throttle=1.0):
        """Advance the crankshaft by dt seconds using its current speed and
        angle, and return the net torque produced during this step.

        load_torque: resistance from drag/friction/load (N*m), opposing
        rotation -- independent of throttle.
        throttle: 0-1, how open the throttle plate is; passed straight
        through to each cylinder's force calculation.
        """
        rpm = self.omega * 60 / (2 * math.pi)
        theta_global_deg = math.degrees(self.theta_rad) % 720

        t_net = self.calculate_net_torque(rpm, theta_global_deg, throttle=throttle)

        alpha = (t_net - load_torque) / self.inertia   # angular acceleration
        self.omega += alpha * dt
        self.theta_rad += self.omega * dt

        return t_net

    def run_frame(self, frame_dt, substeps, load_torque=0.0, throttle=1.0):
        """Advance the crankshaft by one frame's worth of time, split into
        `substeps` small step() calls so fast-changing torque isn't skipped.

        Returns the AVERAGE net torque across the frame's substeps (not
        just the last one) -- torque swings sharply within a single power
        stroke, so the last substep alone is a noisy, misleading sample
        for display/telemetry. The crank's speed and angle are updated in
        place, same as step().
        """
        sub_dt = frame_dt / substeps
        total_t = 0.0
        for _ in range(substeps):
            total_t += self.step(sub_dt, load_torque=load_torque, throttle=throttle)
        return total_t / substeps

    @property
    def rpm(self):
        return self.omega * 60 / (2 * math.pi)


if __name__ == "__main__":
    class DummyCylinder:
        def calculate_downward_force(self, rpm, theta_local=0.0, throttle=1.0):
            return 5000.0 * throttle  # constant placeholder force (N)

    piston = Cylinder(stroke = 84, bore = 71, rod_length=145, compression_ratio=12.5)


    crank = Crankshaft(
        stroke= 84,
        rod_length=145,
        cylinders=[piston for _ in range(2)],
        family="inline",
        layout="I2",
        start_rpm=800,
    )

    # One 60 FPS frame, broken into small sub-steps internally so fast
    # torque changes aren't skipped.
    frame_dt = 1 / 60
    sub_steps = 151
    torque_vals = []
    for step in range(sub_steps):
        crank.step(frame_dt, 0.02)
        torque = crank.calculate_net_torque(crank.rpm, math.degrees(crank.theta_rad))
        torque_vals.append(torque)
        print(f"STEP {step}: rpm = {crank.rpm:7.1f}  torque = {torque:7.1f}")
    print(f"AVERAGE TORQUE: {np.mean(torque_vals):7.1f}  MAX TORQUE: {max(torque_vals):7.1f}  MIN TORQUE: {min(torque_vals):7.1f}")
