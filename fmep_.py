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

def calc_total_displacement():
    displacement = engine.cylinder.surface_area * engine.stroke_m * len(engine.cylinders)
    return displacement

def calc_load_torque(fmep_val):
    load_torque = (fmep_val * 1000 * calc_total_displacement()) / (4 * math.pi)
    return load_torque


#CHENN FLYNN FRICTION CORRELATION INTEGRATED INTO THE HEADLESS SCRIPT
def run(dt:float, substeps:int, throttle_val:float, time_in_seconds:int)-> None:
    elapsed_time = 0
    rpms = []
    load_torque_vals = []
    net_torque_vals = []
    pressure_sets = []
    max_pressure_sets = []
    f_mep_vals = []
    A = 37  # kPa  baseline accessory factor independent of engine speed
    B = 0.006  # no units  gas loading efficiency drop factor by piston pushing against cylinder walls after combustion
    C = 5  # kPa/m/s   scale linearly with speed as trapped oil film is sheared off
    D = 0.1  # kPa/m/s2   scales quadratically with engine speed representing fluid aerodynamic resistance of air/oil mist
    print_step = 0
    while elapsed_time < time_in_seconds:
        N = engine.engine_rpm
        pressures = [(engine.cylinder._combustion_state(i, N, throttle_val))/1000 for i in range(0, 721, 30)]
        p_max = max(pressures)
        N_s = mean_piston_speed(N)
        f_mep = A + B * p_max + C * N_s + D * N_s ** 2
        load_torque = calc_load_torque(f_mep)
        f_mep_vals.append(f_mep)
        if elapsed_time <= 2.0:
            pressure_sets.append(pressures)
            max_pressure_sets.append(p_max)
            rpms.append(N)
        engine.crank.run_frame(dt, substeps, load_torque, throttle_val)
        net_torque = engine.crank.calculate_net_torque(N, theta_global=engine.theta_deg, throttle=throttle_val)
        net_torque_vals.append(net_torque)
        load_torque_vals.append(load_torque)
        print_step += dt
        if print_step >= 1.0:
            print(f"RPM: {N}--- PISTON_SPEED: {N_s}m/s --- LOAD_TORQUE: {load_torque}Nm --- MAX_PRESSURE: {p_max}kPa ---FMEP: {f_mep} kPa")
            print_step -= 1.0
        elapsed_time += dt

    average_rpm = statistics.mean(rpms)
    average_load_torque = statistics.mean(load_torque_vals)
    average_net_torque = statistics.mean(net_torque_vals)
    average_max_pressure = statistics.mean(max_pressure_sets)
    average_f_mep = statistics.mean(f_mep_vals)

    final_mechanical_efficiency = (net_torque_vals[-1] - load_torque_vals[-1]) / net_torque_vals[-1]
    print("RESULTS")
    print(f"AVERAGE(SETTLED) RPM: {round(average_rpm, 1)}RPM")
    print(f"AVERAGE LOAD TORQUE: {round(average_load_torque, 3)}Nm")
    print(f"AVERAGE NET TORQUE: {round(average_net_torque, 3)}Nm")
    print(f"AVERAGE MAX PRESSURE: {round(average_max_pressure, 3)}kPa")
    print(f"AVERAGE FMEP: {round(average_f_mep, 3)}kPa")
    print(f"MECHANICAL EFFICIENCY: {round(final_mechanical_efficiency * 100, 3)}%")


run(1/60,50,0.34,5)



