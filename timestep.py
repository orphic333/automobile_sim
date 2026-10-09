import math
from scipy import constants

timestep = 0.002
g = 9.80665
sea_level_air_density = 1.225  # kg/cubic meter
sea_level_standard_pressure = 101325  # Pa
sea_level_standard_temperature = 288.15  # K
temperature_lapse_rate = 0.0065  # per K
molar_mass_of_dry_air = 0.029854  # kg/mol


def get_atmospheric_properties(altitude):
    """
    Calculates static pressure and air density at a given altitude using the US Standard Atmosphere Model
    (Troposphere Layer)
    :param altitude:
    :return: p_static, density
    """
    altitude = max(0, altitude)

    # Calculate temperature at altitude
    temperature = sea_level_standard_temperature - temperature_lapse_rate * altitude

    temperature = max(1.0, temperature)
    #Barometric formula for static pressure (P_static)
    exponent = (constants.g * molar_mass_of_dry_air) / (constants.R * temperature_lapse_rate)
    p_static = sea_level_standard_pressure * math.pow(
        (1.0 - (temperature_lapse_rate * altitude) / sea_level_standard_temperature), exponent)

    #Ideal gas Law to find density
    density = (p_static * molar_mass_of_dry_air) / (constants.R * temperature)

    return p_static, density, temperature


def freefall_with_drag(altitude, object_mass, cross_sectional_area, drag_coefficient):
    elapsed_time = 0
    vel = 0
    while altitude > 0:
        p_static, density_of_fluid, air_temp = get_atmospheric_properties(altitude)

        p_dynamic = 0.5 * density_of_fluid * (vel ** 2)
        p_total = p_dynamic + p_static

        drag_force = p_dynamic * drag_coefficient * cross_sectional_area
        gravity_force = object_mass * constants.g
        net_force = gravity_force - drag_force
        acceleration = net_force / object_mass
        vel += acceleration * timestep
        altitude -= vel * timestep
        elapsed_time += timestep
        print(
            f"Time elapsed: {elapsed_time:7.2f}s Speed: {vel:.2f}m/s  Altitude: {max(0, altitude):.2f}m   Total Pressure: {p_total:.2f}Pa   Air Temperature: {constants.convert_temperature(air_temp, "Kelvin", "Celsius"):.2f}C")


def freefall(distance):
    elapsed_time = 0
    vel = 0
    while distance > 0:
        vel += g * timestep
        distance -= vel * timestep
        elapsed_time += timestep
        print(f"Time elapsed: {elapsed_time:7.2f}s Speed: {vel:.2f}m/s  Height: {max(0, distance):.2f}m")


freefall_with_drag(11000, 6000, 0.38, 0.12)
