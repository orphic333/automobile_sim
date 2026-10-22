import statistics
from engine import Engine

fun_engine = Engine(
    71,
    84,
    145,
    "inline",
    "I2",
    12.5
)

test_engine = Engine(
    bore= 71,
    stroke= 84,
    rod_length= 151.2,
    family= "inline",
    layout= "I2",
    compression_ratio= 10.5
)


def test(dt, substeps, throttle_val, time_in_seconds):
    elapsed_time = 0
    rpms = []
    torque_vals = []
    starting_rpm = test_engine.engine_rpm
    while elapsed_time < time_in_seconds:
        load_torque = 0.03 * test_engine.engine_rpm
        test_engine.crank.run_frame(dt, substeps, load_torque, throttle_val)
        p_max = test_engine.cylinder._combustion_state(theta_local = 120, current_rpm=test_engine.engine_rpm, throttle=throttle_val)
        rpms.append(test_engine.engine_rpm)
        torque_vals.append(load_torque)
        print(f" RPM: {test_engine.engine_rpm}   TORQUE: {load_torque} MAX PRESSURE: {p_max} ")
        elapsed_time += dt

    final_rpm = rpms[-1]
    assert final_rpm > 600, "FAILED"
    print()
    print("--------RESULTS--------")
    print(f" FINAL RPM: {rpms[-1]}   STARTING RPM: {starting_rpm}")

    print(f"AVERAGE TORQUE: {average_torque}")
    print(f"AVERAGE RPM: {average_rpm}")


test(1/60,50,0.34,10)

