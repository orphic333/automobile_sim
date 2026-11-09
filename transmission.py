import math

from engine import Engine

gear_ratios = (3.62, 2.12, 1.53, 1.12, 0.91, 0.73)


class Transmission:
    def __init__(self, ratios:tuple, engine, car):
        self.engine = engine
        self.car = car
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
            # new crank speed = old crank speed * (new ratio / old ratio)
            new_crank_speed = self.engine_rpm * (self._current_ratio / self.ratios[self.current_gear - 2])
            new_omega = self.pass_speed(new_crank_speed)
            return new_omega
        else:
            print(f"Already at gear {len(self.ratios)}!")
            return self.engine.crank.omega

    def pass_speed(self, crank_speed):
        crank = self.engine.crank
        crank.omega = (crank_speed * 2 * math.pi) / 60
        return crank.omega

    def down_shift(self):
        if self.current_gear > 1:
            self.current_gear -= 1
            new_crank_speed = self.engine_rpm * (self._current_ratio / self.ratios[self.current_gear])
            new_omega = self.pass_speed(new_crank_speed)
            return new_omega
        else:
            print(f"Already at first gear!")
            return self.engine.crank.omega

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
        output_torque = self.engine.engine_torque * self._current_ratio * self.final_drive if self._current_ratio > 0 else 0
        return output_torque

    def reflected_inertia(self):
        m = self.car.mass
        r = self.car.wheel_radius
        denominator = (self._current_ratio * self.final_drive) ** 2
        numerator = m * r**2
        inertia = numerator / denominator
        return inertia

if __name__ == "__main__":
    car_engine = Engine(
        71,
        84,
        145,
        "inline",
        "I2",
        12.5)

    class FakeCar:
        mass = 1000
        wheel_radius = 0.3

    fake_car = FakeCar()
    transmission = Transmission(ratios=gear_ratios, engine=car_engine, car=fake_car)

    print(f" 1 : {car_engine.crank.omega}")
    print(f" 2 : {transmission.up_shift()}")
    print(f" 3 : {transmission.up_shift()}")
    print(f" 4 : {transmission.up_shift()}")
    print(f" 3 : {transmission.down_shift()}")
    print(f" 2 : {transmission.down_shift()}")
    print(f" 1 : {transmission.down_shift()}")



