from engine import Engine

engine = Engine(
    71,
    84,
    145,
    "inline",
    "I2",
    12.5 )
ratios = []
for _ in range(0, 181):
    compression_pressure = engine.cylinder._compression_state(_)
    combustion_pressure = engine.cylinder._combustion_state(_,3000,0)
    pressure_ratio = combustion_pressure / compression_pressure
    ratios.append((pressure_ratio, _))

for ratio in ratios:
    print(f"RATIO: {round(ratio[0], 7)} ANGLE: {ratio[1]}")

