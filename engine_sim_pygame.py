"""
Pygame front end for the Crankshaft/Cylinder simulation.

Keyboard controls:
  UP ARROW / W   - throttle: hold to open the throttle and rev the engine
                   released (no key held) the engine idles
  ESC or window close - quit

This file only drives the simulation loop and handles input/display.
All physics stays in crankshaft.py / piston.py.
"""

import sys
import pygame

from engine import Engine


def build_engine(bore, stroke, rod_length, family, layout, compression_ratio):
    engine = Engine(
        bore=bore,
        stroke=stroke,
        rod_length=rod_length,
        family=family,
        layout=layout,
        compression_ratio=compression_ratio,
    )
    return engine


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 240))
    pygame.display.set_caption("Engine Sim")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28)

    crank = build_crankshaft()

    FPS = 60
    SUBSTEPS = 50
    BASE_LOAD_COEFF = 0.02      # friction/drag, independent of throttle, scales with rpm
    IDLE_THROTTLE = 0.34       # throttle plate barely cracked open, same as a real idling engine

    # Exponential moving average smoothing for the on-screen numbers only.
    # The physics itself still runs at full substep resolution underneath --
    # this just keeps the fast-swinging per-frame torque readable.
    SMOOTHING = 0.15
    smoothed_rpm = crank.rpm
    smoothed_torque = 0.0

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
        throttling = keys[pygame.K_UP] or keys[pygame.K_w]

        # --- 2. Advance physics by one frame ---
        # clock.tick() both caps the frame rate AND returns the elapsed
        # time (ms) since the previous call, in one step -- using it
        # directly avoids a stale/lagged dt reading.
        frame_dt = clock.tick(FPS) / 1000.0 or (1 / FPS)
        if throttling:
            throttle += throttle_speed * frame_dt  #
        else:
            throttle -= throttle_speed * frame_dt
        throttle = max(IDLE_THROTTLE, min(throttle, 1.0))
        load_torque = BASE_LOAD_COEFF * crank.rpm
        net_torque = crank.run_frame(frame_dt, SUBSTEPS, load_torque=load_torque, throttle=throttle)

        smoothed_rpm += (crank.rpm - smoothed_rpm) * SMOOTHING
        smoothed_torque += (net_torque - smoothed_torque) * SMOOTHING

        # --- 3. Draw ---
        screen.fill((20, 20, 20))
        rpm_text = font.render(f"RPM: {smoothed_rpm:7.1f}", True, (255, 255, 255))
        torque_text = font.render(f"Torque: {smoothed_torque:7.1f} N*m", True, (200, 200, 200))
        throttle_text = font.render(
            f"Throttle: {'FULL' if throttling else 'idle'}", True, (160, 160, 160)
        )
        hint_text = font.render("Hold UP/W to throttle, ESC to quit", True, (120, 120, 120))
        screen.blit(rpm_text, (20, 40))
        screen.blit(torque_text, (20, 80))
        screen.blit(throttle_text, (20, 120))
        screen.blit(hint_text, (20, 180))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
