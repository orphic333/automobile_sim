from engine import Engine
from transmission import Transmission

class Car:
    def __init__(self,
                 bore:float,
                 stroke:float,
                 rod_length:float,
                 family: str,
                 layout: str,
                 ratios: tuple,
                 mass: float,
                 wheel_radius: float,
                 compression_ratio:float = 10.0,
                 ):
        self.mass = mass
        self.wheel_radius = wheel_radius
        self.engine = Engine(stroke=stroke, bore=bore, rod_length=rod_length, compression_ratio=compression_ratio, family=family, layout=layout)
        self.transmission = Transmission(ratios=ratios, engine=self.engine, car=self)



