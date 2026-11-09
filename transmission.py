from engine import Engine

gear_ratios = (3.62, 2.12, 1.53, 1.12, 0.91, 0.73)


class Transmission:
    def __init__(self, ratios:tuple, engine:Engine):
        self.engine = engine
        if ratios is None:
            raise ValueError("ratios must be specified")
        self.ratios = ratios
        if self.engine_rpm <= 0:
            raise ValueError("engine_rpm must be greater than 0")

        self.current_gear = 1  #1st gear
        self.final_drive = 3.92 #final drive

    def up_shift(self):

        if self.current_gear < len(self.ratios):
            self.current_gear += 1
            return self.current_gear
        else:
            print(f"Already at gear {len(self.ratios)}!")
            return self.current_gear

    def down_shift(self):
        if self.current_gear > 1:
            self.current_gear -= 1
            new_crank_speed = self.engine_rpm * (self._current_ratio / self.ratios[self.current_gear])
            new_omega = self.pass_speed(new_crank_speed)
            return new_omega
        else:
            print(f"Already at first gear!")
            return self.current_gear

    @property
    def engine_torque(self) -> float:
        return self.engine.engine_torque

    @property
    def engine_rpm(self):
        return self.engine.engine_rpm

    @property
    def _current_ratio(self):
        return self.ratios[self.current_gear - 1]

    @property
    def wheel_output_rpm(self):
        wheel_rpm = self.engine_rpm / (self._current_ratio * self.final_drive) if self._current_ratio > 0 else 0
        return wheel_rpm

    @property
    def output_torque(self):
        output_torque = self.engine.engine_torque * self._current_ratio
        return output_torque

    def reflected_inertia(self):
        m = self.car.mass
        r = self.car.wheel_radius
        denominator = (self._current_ratio * self.final_drive) ** 2
        numerator = m * r**2
        inertia = numerator / denominator
        return inertia

if __name__ == "__main__":
    car1_engine = Engine(
        bore= 100,
        stroke= 80,
        rod_length= 60,
        family= "inline",
        layout= "I2",
        compression_ratio= 12,
    )
    car1_Transmission = Transmission(gear_ratios, car1_engine)
    print(car1_engine.theta_deg)  #initialised to 0.00
    print(car1_engine.engine_rpm)  #initialised to 800 rpm
    print(car1_Transmission.engine_torque)
    print(car1_Transmission.output_torque)
