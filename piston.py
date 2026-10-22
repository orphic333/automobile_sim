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

    # Wiebe function constants: how combustion actually spreads over a span
    # of crank rotation instead of happening all at once. BURN_DURATION_DEG
    # is how many degrees of crank angle the burn takes; WIEBE_A/WIEBE_N
    # shape the burn curve (these are the standard textbook defaults).
    BURN_DURATION_DEG = 40.0
    WIEBE_A = 5.0
    WIEBE_N = 3.0

    def __init__(self, bore, stroke, rod_length=140.0, compression_ratio=10.0):
        """
        bore, stroke, rod_length: millimeters
        compression_ratio: dimensionless (V_at_bdc / V_at_tdc)
        """
        self.bore_m = bore/1000
        self.stroke_m = stroke/1000
        self.rod_length_m = rod_length/1000
        self.compression_ratio = compression_ratio

        self.swept_volume = self._calculate_swept_volume()
        self.surface_area = math.pi * (self.bore_m /2) ** 2
        # Clearance volume: what's left at TDC when the full swept volume
        # has been compressed away. CR = (Vswept + Vclearance) / Vclearance.
        self.clearance_volume = self.swept_volume / (compression_ratio - 1)
        self.volume_at_bdc = self.clearance_volume + self.swept_volume

        # A fixed reference mass (kg) -- "how much a cylinder-full of air at
        # intake conditions would weigh". This isn't the actual trapped
        # mass (that's derated by VE/throttle); it's a constant unit-
        # conversion anchor so pressure can be computed directly from
        # temperature and volume via the ideal gas law, same way for both
        # strokes below.
        self._reference_mass = (
            self.INTAKE_PRESSURE * self.volume_at_bdc
            / (self.GAS_CONSTANT * self.INTAKE_TEMP)
        )

    def _calculate_swept_volume(self):
        swept_volume = math.pi  * (self.bore_m / 2) ** 2 *  self.stroke_m
        return swept_volume

    @staticmethod
    def _calculate_synthetic_volumetric_efficiency(current_rpm, peak_ve = 0.85, peak_rpm = 4500.0, sigma = 3500.0):
        """
       Calculates the volumetric efficiency of an engine cylinder dynamically using Gaussian Distribution
        """
        exponent = -((current_rpm - peak_rpm) ** 2 ) /  (2 * (sigma ** 2))
        ve = peak_ve * np.exp(exponent)
        return ve

    def _piston_position(self, theta_local_deg):
        """
        Distance (m) the piston has traveled from TDC, at crank angle
        theta_local_deg (0 = TDC, 180 = BDC), via the slider-crank formula.
        r = crank radius (half the stroke), l = connecting rod length.
        Trig functions are periodic, so this is valid for any angle, not
        just 0-180 -- the same formula naturally covers the compression
        stroke (180-360) too.
        """
        r_m = self.stroke_m / 2
        l_m = self.rod_length_m
        theta = math.radians(theta_local_deg)
        return r_m + l_m - (r_m * math.cos(theta) + math.sqrt(l_m**2 - (r_m * math.sin(theta))**2))

    def _instantaneous_volume(self, theta_local_deg):
        """Cylinder volume (m^3) above the piston at this crank angle."""
        return self.clearance_volume + self._piston_position(theta_local_deg) * self.surface_area

    def _compression_state(self, theta_local):
        """
        Pressure (Pa) during the compression stroke (540-720 in the full
        720-degree cycle). Pure isentropic compression -- no fuel involved
        yet, so no RPM/throttle dependence, just geometry: P * V^gamma is
        constant from the intake state to wherever the piston is now.
        """
        v_now = self._instantaneous_volume(theta_local)
        return self.INTAKE_PRESSURE * (self.volume_at_bdc / v_now) ** self.GAMMA

    def _wiebe_fraction(self, theta_since_ignition):
        """
        Fraction of the fuel's energy released so far, theta_since_ignition
        degrees after ignition starts. 0 before ignition, rising smoothly
        to 1 by the end of BURN_DURATION_DEG -- this is what actually
        spreads combustion out over a span of crank rotation instead of
        dumping all the heat in at a single instant.
        """
        if theta_since_ignition <= 0:
            return 0.0
        if theta_since_ignition >= self.BURN_DURATION_DEG:
            return 1.0
        x = theta_since_ignition / self.BURN_DURATION_DEG
        return 1 - math.exp(-self.WIEBE_A * x ** (self.WIEBE_N + 1))

    def _burn_state(self, theta_local, rpm, throttle_val=1.0):
        t2 = self.INTAKE_TEMP * self.compression_ratio ** (self.GAMMA - 1)
        ve = self._calculate_synthetic_volumetric_efficiency(rpm) * throttle_val
        fuel_fraction = 1 / (self.AIR_FUEL_RATIO + 1)
        q_in = fuel_fraction * self.LOWER_HEATING_VALUE * ve
        cv = self.GAS_CONSTANT / (self.GAMMA - 1)
        ratio = q_in / cv
        start = 0
        t_now = t2
        while start < theta_local:
            # t2, instantaneous volume, wiebe fraction, q_in/cv
            end = min(start + 1, theta_local)
            x = self._wiebe_fraction(end)
            x_prev = self._wiebe_fraction(start)
            v_now = self._instantaneous_volume(end)
            v_prev = self._instantaneous_volume(start)
            t_now *= (v_prev / v_now) ** (self.GAMMA - 1)
            energy_released = (x - x_prev) * ratio
            t_now += energy_released
            start = end
        return t_now


    def _combustion_state(self, theta_local, current_rpm, throttle):
        """
        Pressure (Pa) during the power stroke (0-180). Ignition happens at
        TDC (theta_local=0); heat is released progressively through the
        burn window per _wiebe_fraction, with the piston already moving
        outward as it burns -- so pressure rises to a peak somewhere after
        TDC, not exactly at it, same as a real engine. After the burn
        finishes, the hot gas just expands adiabatically (no more heat
        being added), handled as isentropic expansion from the end-of-burn
        state.
        """

        if theta_local < self.BURN_DURATION_DEG:
            # Still burning: heat added so far raises temperature; volume
            # is whatever the piston's kinematics say at this angle.
            t_now = self._burn_state(theta_local, current_rpm, throttle)
            v_now = self._instantaneous_volume(theta_local)
            v_specific = v_now / self._reference_mass
            return self.GAS_CONSTANT * t_now / v_specific

        # Burn finished: no more heat coming in, so from here it's pure
        # isentropic expansion from the end-of-burn state.
        t_end = self._burn_state(self.BURN_DURATION_DEG, current_rpm, throttle)
        v_end = self._instantaneous_volume(self.BURN_DURATION_DEG)
        v_specific_end = v_end / self._reference_mass
        p_end = self.GAS_CONSTANT * t_end / v_specific_end

        v_now = self._instantaneous_volume(theta_local)
        return p_end * (v_end / v_now) ** self.GAMMA

    def calculate_downward_force(self, current_rpm, theta_local=0.0, throttle=1.0):
        """
        theta_local: crank angle (degrees) within this cylinder's own
        720-degree cycle (0 = TDC at the start of the power stroke).
        throttle: 0-1, how open the throttle plate is -- restricts trapped
        charge, same as a real idling engine.

        Returns force (N) during the power stroke (0-180, combustion then
        expansion) and the compression stroke (540-720, the piston doing
        work ON the gas before ignition). Zero during intake/exhaust
        (180-540) -- those strokes still aren't modeled, a simplification
        that's still on the books.
        """
        if 0 <= theta_local < 180:
            pressure = self._combustion_state(theta_local, current_rpm, throttle)
        elif 540 <= theta_local < 720:
            pressure = self._compression_state(theta_local)
        else:
            return 0.0

        return round(pressure * self.surface_area, 3)

if __name__ == '__main__':
    cylinder = Cylinder(stroke=92.9, bore=153.5)
    for i in range(0,720,30):
        print(cylinder.calculate_downward_force(3000, i))