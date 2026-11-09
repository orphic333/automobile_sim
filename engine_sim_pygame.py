"""
Pygame front end for the Crankshaft/Cylinder simulation.

Keyboard controls:
  UP ARROW / W   - throttle: hold to open the throttle and rev the engine
                   released (no key held) the engine idles
  ESC or window close - quit

This file only drives the simulation loop and handles input/display.
All physics stays in crankshaft.py / piston.py.
"""
import math
import sys
import pygame

import constants
from fmep_class_ import Fmep
from car import Car

def build_car(bore,stroke,rod_length,family,layout,ratios,mass,wheel_radius,compression_ratio):
    user_car = Car(
        bore=bore,
        stroke=stroke,
        rod_length=rod_length,
        family=family,
        layout=layout,
        ratios = ratios,
        mass=mass,
        wheel_radius=wheel_radius,
        compression_ratio=compression_ratio
    )
    return user_car

def main():
    #   INPUT FROM USERS COLLECTED AND VALIDATED IN A BLOCK ABOVE. INPUTS THEN PASSED TO THE build_engine() function BELOW.
    #   LATER FEATURE.
    user_car = build_car(
        71,
        84,
        145,
        "inline",
        "I2",
        (3.62, 2.12, 1.53, 1.12, 0.91, 0.73),
        1000,
        0.3,
        12.5
    )

    car_engine = user_car.engine
    car_transmission = user_car.transmission
    fmep = Fmep(car_engine)
    pygame.init()
    screen = pygame.display.set_mode((840, 640))
    pygame.display.set_caption("Engine Sim")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28)

    crank = car_engine.crank

    FPS = constants.FPS
    SUBSTEPS = constants.SUBSTEPS
    IDLE_THROTTLE = 0.07572509851086025  # throttle plate barely cracked open, same as a real idling engine
    S = 2986
    TARGET_TIME_FOR_CORRECTION = constants.TARGET_TIME_FOR_CORRECTION
    GAIN = 1 / (TARGET_TIME_FOR_CORRECTION * S)
    THROTTLE_MIN = 0.01 * IDLE_THROTTLE
    PISTON_SPEED_CAP = 25
    LIMIT_FADE_WIDTH = 300
    rpm_cap = (60 * PISTON_SPEED_CAP) / (2 * car_engine.stroke_m)


    # Exponential moving average smoothing for the on-screen numbers only.
    # The physics itself still runs at full substep resolution underneath --
    # this just keeps the fast-swinging per-frame torque readable.
    SMOOTHING = constants.SMOOTHING
    smoothed_rpm = crank.rpm
    # Dial drawing constants
    smoothed_torque = 0.0
    sweep = 270
    start = 225
    max_rpm = 10000
    length = 75
    cx, cy = 380, 400
    base = 20

    running = True
    throttle = 0.00
    throttle_speed = 0.9
    while running:
        # --- 1. Handle input/events (checked every frame) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        pedal_throttling = keys[pygame.K_UP] or keys[pygame.K_w]

        # --- 2. Advance physics by one frame ---
        # clock.tick() both caps the frame rate AND returns the elapsed
        # time (ms) since the previous call, in one step -- using it
        # directly avoids a stale/lagged dt reading.
        frame_dt = clock.tick(FPS) / 1000.0 or (1 / FPS)
        pedal = throttle
        if pedal_throttling:
            pedal += throttle_speed * frame_dt
            pedal = max(0, min(pedal, 1))
        else:
            pedal -= throttle_speed * frame_dt
        diff = smoothed_rpm - 800
        req_charge = GAIN * diff
        passive_throttle = IDLE_THROTTLE - req_charge
        passive_throttle = max(THROTTLE_MIN, passive_throttle)
        throttle = max(pedal, passive_throttle)
        rpm = crank.rpm
        #mps = 2 * car_engine.stroke_m * rpm / 60
        #rpm = 60 * mps / 2 * car_engine.stroke_m
        cap =  max(0, min((rpm_cap - rpm) / LIMIT_FADE_WIDTH, 1))
        final_throttle = min(throttle, cap)
        load_torque = fmep.calc_load_torque(throttle=final_throttle,dt=frame_dt)
        reflected_inertia = car_transmission.reflected_inertia()
        net_torque = crank.run_frame(frame_dt, reflected_inertia, substeps= SUBSTEPS, load_torque=load_torque, throttle=final_throttle)


        smoothed_rpm += (crank.rpm - smoothed_rpm) * SMOOTHING
        smoothed_torque += (net_torque - smoothed_torque) * SMOOTHING

        # --- 3. Draw ---
        screen.fill((20, 20, 20))
        rpm_text = font.render(f"RPM: {smoothed_rpm:7.1f}", True, (255, 255, 255))
        torque_text = font.render(f"Torque: {smoothed_torque:7.1f} N*m", True, (200, 200, 200))
        throttle_text = font.render(
            f"Throttle: {final_throttle:.3f}", True, (160, 160, 160)
        )
        hint_text = font.render("Hold UP/W to throttle, ESC to quit", True, (120, 120, 120))
        # Draw dial
        frac = max(0, min(smoothed_rpm / max_rpm, 1))
        dial_angle = math.radians(start - frac * sweep)
        tip = pygame.math.Vector2(cx + length * math.cos(dial_angle), cy - length * math.sin(dial_angle))
        back_left = pygame.math.Vector2(
            cx + (base/2) * math.cos(dial_angle + math.pi/2), cy - (base/2) * math.sin(dial_angle + math.pi/2)
        )
        back_right = pygame.math.Vector2(
            cx + (base/2) * math.cos(dial_angle - math.pi/2), cy - (base/2) * math.sin(dial_angle - math.pi/2)
        )
        triangle_points = [tip, back_left, back_right]

        dial_max = max_rpm / 1000
        for k in range(0, math.ceil(max_rpm/1000) + 1):
            fraction = k / (max_rpm /1000)
            angle = math.radians(start - fraction * sweep)
            label = pygame.math.Vector2(cx + 105 * math.cos(angle), cy - 105 * math.sin(angle))
            for j in range(5):
                value = k + j/5
                if value > dial_max:
                    break
                color = 'white' if value <= (rpm_cap-LIMIT_FADE_WIDTH)/1000 else 'red'
                end_pos_val = 80 if j == 0 else 85
                fract = value / dial_max
                angle = math.radians(start - fract * sweep)
                start_pos = pygame.math.Vector2(cx + 90 * math.cos(angle), cy - 90 * math.sin(angle))
                end_pos = pygame.math.Vector2(cx + end_pos_val * math.cos(angle), cy - end_pos_val * math.sin(angle))
                pygame.draw.line(screen, color, start_pos, end_pos)
            text = font.render(f"{k}", True, 'blue')
            rect = text.get_rect(center =(label.x, label.y))
            screen.blit(text, rect)





        pygame.draw.polygon(screen, 'blue', triangle_points, width=1)
        pygame.draw.circle(screen, 'white', (cx, cy), 3)
        pygame.draw.circle(screen, 'white', (cx,cy), 125, width=5)
        screen.blit(rpm_text, (20, 40))
        screen.blit(torque_text, (20, 80))
        screen.blit(throttle_text, (20, 120))
        screen.blit(hint_text, (20, 180))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
