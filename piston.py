#Ultimate goal is to create a car object that can receive inputs to move. It's motion should be based on real physical
# properties cars possess. In essence, a car simulation written entirely by me (kind of). You can split the car into major
# parts like the drivetrain, engine, chassis (frame, suspension, steering, braking, wheels and tires)
#Let's get into the fundamental physics. We'll take it one at a time.
#Objective 1: Build an engine.
#-----ENGINE--------------
#In order to do work, you need energy.
#Energy is from the engine by means of (a) combustion (b) electricity (c) (a) and (b)
#Considering combustion engines...
#Energy = Force * distance travelled by force (turning force via pistons connected to crankshaft)
#Amount of power the engine produces is the car's horsepower which varies with throttle input.
#Maximum amount of power would correspond to peak horsepower.
#Torque refers to the twisting force a car is capable of producing or produces
#Horsepower is how fast that work can be done.
#HORSEPOWER = (TORQUE (lb-ft) * RPM) / 5252
#Analogy: in turning a crank, person A can twist the crank with 800N through a distance x. Person B can twist it with a
# maximum of 500N.
#Person B can maintain that twisting force for longer as speed increases.
#Person A can't. The twisting force drops significantly in order for him to turn the crank faster.
#Person A has high torque, low horsepower
#Person B has high horsepower, low torque (in relation to Person A)
#-----INSIDE THE ENGINE-------- (assuming it is ideal)
#-----PISTON------
# F(piston) = mean effective pressure * piston area.
# TORQUE = F(piston) * crankshaft offset throw (r) [offset from the crankshaft's center]
# The cylinder has a bore and a stroke.
# The bore is its internal diameter. You could say its width.
# The stroke is the distance it travels from TDC(Top Dead Center) to BDC(Bottom Dead Center)
# Bore to Stroke Ratio produces different results in engine performance (Undersquare, Oversquare, Square)
# Engine displacement (volume) is the swept volume of a single cylinder
# It is given by pi * (bore/2)**2 * L (stroke)
# Volumetric Efficiency (VE) is the percentage of the ratio of air sucked in during the intake stroke, and the theoretical
# max volume
# Thus, TORQUE = P (mean effective pressure) * pi * (bore/2)**2 * crank radius
# Adding more cylinders with the same swept volume doesn't increase torque. Rather, it lifts the curve closer to its
# peak over lower RPM's.
# I can reverse engineer a factory torque array to get a VE array with this formula:
# VE = TORQUE * 4 * pi * Air-Fuel Ratio / Density of Air * Engine displacement * Heating Value of Fuel * Thermal Efficiency
# Optional: Torsional stiffness is how much the crankshaft twists under instantaneous torque of a combustion event.
# It is given by Kt = G * J / L
# G is the shear modulus of the material (for example, steel)
# L is the length of the crankshaft
# J is the polar moment of inertia of the shaft's cross-section
# The stiffness affects resonant frequency: wn = sqr root ( Kt / inertia of crank)
# Higher stiffness means higher resonant frequency which translates to higher RPM's.
# Lower engine center of mass influences the total center of gravity of the vehicle. Lateral load transfer (deltaW)
# dictates how much weight shifts from the inside tires to the outside tires in cornering.
# Optional : deltaW = mass of vehicle * lateral acceleration * height of center of gravity / track width of vehicle
# Optional: Polar moment of inertia can be understood by the resistance the car has to rotating into a corner.
# An example would be turning a heavy truck and turning a mini-car.
# For each component, it could be computed as the mass of the component * distance from vehicle's center of gravity
# Summation of the above would result in the total polar moment of inertia.
# Minimizing this inertia would result in higher angular acceleration from the front tires for a given steering torque
# per Newton's Second law of rotation.
# I should build a cylinder class which would create and manage cylinder objects
# A crankshaft class could also be included to create and manage a crankshaft object that would respond to the cylinder objects.
# Cylinder inputs could be the bore and stroke, and would calculate the swept volume and mean effective pressure. The crankshaft would take the force from the cylinders and calculate the total torque output of the engine.


import math
import numpy as np

class Cylinder:
    # Air-standard Otto cycle constants (shared by every cylinder instance).
    GAMMA = 1.35                   # specific heat ratio of hot combustion gas
    GAS_CONSTANT = 287.0           # J/(kg*K), specific gas constant for air
    INTAKE_PRESSURE = 101_325.0    # Pa, ambient/intake pressure
    INTAKE_TEMP = 300.0            # K, intake charge temperature
    AIR_FUEL_RATIO = 14.7          # stoichiometric, by mass
    LOWER_HEATING_VALUE = 44_000_000.0  # J/kg, gasoline

    def __init__(self, bore, stroke, rod_length=140.0, compression_ratio=10.0):
        """
        bore, stroke, rod_length: millimeters
        compression_ratio: dimensionless (V_at_bdc / V_at_tdc)
        """
        self.bore = bore/1000
        self.stroke = stroke/1000
        self.swept_volume = self._calculate_swept_volume()
        self.surface_area = math.pi * (self.bore /2) ** 2

    def _calculate_swept_volume(self):
        swept_volume = math.pi  * (self.bore / 2) ** 2 *  self.stroke
        return swept_volume

    @staticmethod
    def _calculate_synthetic_volumetric_efficiency(current_rpm, peak_ve = 0.85, peak_rpm = 4500.0, sigma = 3500.0):
        """
       Calculates the volumetric efficiency of an engine cylinder dynamically using Gaussian Distribution
        """
        exponent = -((current_rpm - peak_rpm) ** 2 ) /  (2 * (sigma ** 2))
        ve = peak_ve * np.exp(exponent)
        return ve

    @staticmethod
    def _calculate_mean_effective_pressure(ve_value):
        density_of_air = 1.225 #in kg/cubic meter
        lower_heating_value_gasoline = 44000000 #specific energy of fuel in Joules/kg
        thermal_efficiency = 0.35 #energy that is actually translated into movement
        air_fuel_ratio = 14.7  #14.7:1 (by mass)
        mean_effective_pressure = density_of_air * ve_value * lower_heating_value_gasoline * thermal_efficiency / air_fuel_ratio
        return mean_effective_pressure

    @staticmethod
    def _calculate_crank_angle_pressure_factor(theta_local, peak_angle=15.0,
                                                sigma_rise=10.0, sigma_fall=45.0):
        """
        Scales mean effective pressure by where the piston is within its
        power stroke (theta_local in degrees, 0-180). Real cylinder
        pressure spikes shortly after ignition (near top dead center) and
        decays more slowly as the gas expands, so this uses an asymmetric
        Gaussian: a narrow rise before `peak_angle`, a wider fall after it.
        Returns a 0-1 factor.
        """
        if theta_local < peak_angle:
            sigma = sigma_rise
        else:
            sigma = sigma_fall
        exponent = -((theta_local - peak_angle) ** 2) / (2 * sigma ** 2)
        return math.exp(exponent)

    def calculate_downward_force(self, current_rpm, theta_local=0.0, throttle=1.0):
        """
        theta_local: crank angle (degrees) within this cylinder's own
        power stroke (0-180). Shapes the force to rise and fall across the
        stroke instead of staying constant.
        throttle: 0-1, how open the throttle plate is. Physically this
        restricts how much air reaches the cylinder, so it scales
        volumetric efficiency directly -- a nearly-closed throttle starves
        the engine of air/fuel and produces little force, same as a real
        idling engine.
        """
        ve_value = self._calculate_synthetic_volumetric_efficiency(current_rpm) * throttle
        mean_effective_pressure = self._calculate_mean_effective_pressure(ve_value)
        pressure_factor = self._calculate_crank_angle_pressure_factor(theta_local)
        linear_force_vector = mean_effective_pressure * pressure_factor * self.surface_area
        return round(linear_force_vector, 3)
