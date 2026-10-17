import math

from crankshaft import Crankshaft, CONFIGS
from piston import Cylinder


class Engine:

    def __init__(self, bore:float, stroke:float, rod_length:float, family: str, layout: str, compression_ratio:float = 10.0):
        """
        Assemble crankshaft and cylinder instances into one engine object
        Arguments:
            bore (float): Bore length in millimeters
            stroke (float): Distance traveled by piston from TDC to BDC in millimeters
            rod_length (float): Length in millimeters of connecting rod of piston
            family (str): The family of the configuration
            layout (str): The layout of the family
            compression_ratio (float): How much piston squeezes the air in the cylinder, expressed as a ratio

        The class builds a number of cylinder objects and a crankshaft object dynamically
        """
        if rod_length <= stroke / 2:
            raise ValueError("rod_length must be greater than the crank radius")
        if bore <= 0 or stroke <= 0:
            raise ValueError("bore/stroke must be greater than 0")

        self.offsets = CONFIGS[family][layout]
        self.bore_m = bore / 1000
        self.stroke_m = stroke / 1000
        self.crank_radius_m = stroke / 2000
        self.family = family
        self.layout = layout
        self.rod_length_m = rod_length / 1000
        self.compression_ratio = compression_ratio
        self.cylinder = Cylinder(stroke=stroke, bore=bore, rod_length=rod_length, compression_ratio=compression_ratio)
        self.cylinders = [Cylinder(stroke=stroke, bore=bore, rod_length=rod_length, compression_ratio=compression_ratio) for _ in range(len(self.offsets))]
        self.crank = Crankshaft(stroke=stroke, rod_length=rod_length, cylinders= self.cylinders, family=family, layout=layout)

    @property
    def theta_deg(self):
        return self.crank.theta_rad * 180 / math.pi

    @property
    def engine_rpm(self) -> float:
        return self.crank.rpm

    @property
    def engine_torque(self) -> float:
        return self.crank.calculate_net_torque(current_rpm=self.engine_rpm, theta_global=self.theta_deg)

    def __repr__(self) -> str:
        return f"Engine(layout={self.layout})"

if __name__ == "__main__" :
    engine = Engine(
        bore= 100,
        stroke= 80,
        rod_length= 150,
        family= "inline",
        layout= "I4",
        compression_ratio= 12,
    )
    print(engine.theta_deg)
    print(engine.engine_rpm)
    print(engine)

    for offset, cylinder in zip(engine.offsets, engine.cylinders):
        local_angle = 150 + offset
        force = cylinder.calculate_downward_force(3000, local_angle)
        leverage = engine.crank._leverage(local_angle)
        torque_contribution = force * leverage * engine.crank_radius_m
        piston_position = cylinder._piston_position(local_angle) * 1000
        print(f"LOCAL ANGLE: {local_angle} degrees   FORCE: {force}N   LEVERAGE: {leverage}   TORQUE: {torque_contribution}Nm   POSITION: {piston_position}mm")
