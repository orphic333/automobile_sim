import math

from engine import Engine

class Fmep:
    A = 37  # kPa  baseline accessory factor independent of engine speed
    B = 0.006  # no units  gas loading efficiency drop factor by piston pushing against cylinder walls after combustion
    C = 5  # kPa/m/s   scale linearly with speed as trapped oil film is sheared off
    D = 0.1  # kPa/ms2   scales quadratically with engine speed representing fluid aerodynamic resistance of air/oil mist
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_rpm(self):
        return self.engine.engine_rpm

    def mean_piston_speed(self):
        p_s = (2 * self.engine.stroke_m * self.get_rpm()) / 60
        return p_s

    def calc_total_displacement(self):
        displacement = self.engine.cylinder.surface_area * self.engine.stroke_m * len(self.engine.cylinders)
        return displacement

    def get_max_pressure(self, throttle):
        return self.engine.cylinder.max_pressure(self.engine.engine_rpm, throttle=throttle)

    def calc_fmep(self, throttle):
        N_s = self.mean_piston_speed()
        p_max = self.get_max_pressure(throttle=throttle)
        fmep = self.A + self.B * p_max + self.C * N_s + self.D * N_s ** 2
        return fmep

    def calc_load_torque(self, throttle, dt):
        load_torque = (self.calc_fmep(throttle=throttle) * 1000 * self.calc_total_displacement()) / (4 * math.pi)
        cap = self.engine.crank.omega * (self.engine.crank.inertia / dt)
        load_torque = min(cap, load_torque)
        return load_torque

if __name__ == "__main__":
    car_engine = Engine(
        71,
        84,
        145,
        "inline",
        "I2",
        12.5)
    fmep = Fmep(car_engine)


    def run(dt: float, substeps: int, throttle_val: float, time_in_seconds: int) -> None:
        elapsed_time = 0
        while elapsed_time < time_in_seconds:
            load_torque = fmep.calc_load_torque(throttle=throttle_val, dt=dt)
            average_torque = car_engine.crank.run_frame(dt, substeps, load_torque, throttle_val)
            print(f"RPM: {car_engine.engine_rpm}    LOAD TORQUE: {load_torque:.3f}      INDICATED TORQUE: {average_torque:.3f}")
            elapsed_time += dt

    run(1/60, 75, 0.07572509851086025, 6)

