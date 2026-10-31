import math
import statistics

from engine import  Engine
engine = Engine(
    71,
    84,
    145,
    "inline",
    "I2",
    12.5 )

def mean_piston_speed(rpm):
    s_p = (2 * engine.stroke_m * rpm) / 60
    return s_p

def calc_total_displacement(engine):
    displacement = engine.cylinder.surface_area * engine.stroke_m * len(engine.cylinders)
    return displacement

def calc_load_torque(fmep_val, engine):
    load_torque = (fmep_val * 1000 * calc_total_displacement(engine)) / (4 * math.pi)
    return load_torque

def fmep_factors():
    return A,B,C,D
A = 37  # kPa  baseline accessory factor independent of engine speed
B = 0.006  # no units  gas loading efficiency drop factor by piston pushing against cylinder walls after combustion
C = 5  # kPa/m/s   scale linearly with speed as trapped oil film is sheared off
D = 0.1  # kPa/ms2   scales quadratically with engine speed representing fluid aerodynamic resistance of air/oil mist


#CHENN FLYNN FRICTION CORRELATION INTEGRATED INTO THE HEADLESS SCRIPT
def run(dt:float, substeps:int, throttle_val:float, time_in_seconds:int)-> None:
        elapsed_time = 0
        rpms = []
        load_torque_vals = []
        indicated_torque_vals = []
        max_pressure_sets = []
        f_mep_vals = []
        while elapsed_time < time_in_seconds:
            N = engine.engine_rpm
            pressures = [(engine.cylinder._combustion_state(i, N, throttle_val))/1000 for i in range(0, 181)]
            p_max = max(pressures)
            N_s = mean_piston_speed(N)
            f_mep = A + B * p_max + C * N_s + D * N_s ** 2
            load_torque = calc_load_torque(f_mep, engine)
            cap = engine.crank.omega * (engine.crank.inertia / dt)
            load_torque = min(cap, load_torque)
            f_mep_vals.append(f_mep)   # data collection step
            if elapsed_time >= time_in_seconds - 2.0:
                max_pressure_sets.append(p_max)  # data collection step
                rpms.append(N)   # data collection step
            average_torque = engine.crank.run_frame(dt, substeps, load_torque, throttle_val)
            #   net_torque = engine.crank.calculate_net_torque(N, theta_global=engine.theta_deg, throttle=throttle_val)
            indicated_torque_vals.append(average_torque) # data collection step
            load_torque_vals.append(load_torque)   # data collection step
            print(
                f" RPM: {N}       MEAN TORQUE: {statistics.mean(indicated_torque_vals)}      LOAD TORQUE: {load_torque}")
            elapsed_time += dt

        average_rpm = statistics.mean(rpms)
        average_load_torque = statistics.mean(load_torque_vals)
        average_indicated_torque = statistics.mean(indicated_torque_vals)
        average_max_pressure = statistics.mean(max_pressure_sets)
        average_f_mep = statistics.mean(f_mep_vals)
        mechanical_efficiency = (average_indicated_torque - average_load_torque) / average_indicated_torque if average_indicated_torque > 0 else None
        print(f"AVERAGE LOAD TORQUE: {average_load_torque}\n"
              f"AVERAGE INDICATED TORQUE: {average_indicated_torque}\n"
              f"AVERAGE RPM: {average_rpm}")
if __name__ == "__main__":
    run(1/60, 75, 0.07572509851086025, 6)





