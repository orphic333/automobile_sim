"""
Pygame front end for the Crankshaft/Cylinder simulation.

Keyboard controls:
  UP ARROW / W   - throttle: hold to request more load torque resistance
                   released (no key held) the engine coasts against idle load
  ESC or window close - quit

This file only drives the simulation loop and handles input/display.
All physics stays in crankshaft.py / car_practice.py.
"""

import sys
import pygame

from crankshaft import Crankshaft
from piston import Cylinder


def build_crankshaft():
    cylinders = [Cylinder(86, 86) for _ in range(4)]
    return Crankshaft(
        stroke=0.086,
        rod_length=0.145,
        cylinders=cylinders,
        family="inline",
        layout="I4",
        start_rpm=800,
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 240))
    pygame.display.set_caption("Engine Sim")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28)

    crank = build_crankshaft()

    FPS = 60
    SUBSTEPS = 50
    BASE_LOAD_COEFF = 0.02   # idle friction/drag, scales with rpm
    THROTTLE_LOAD_COEFF = 0.12  # extra resistance while "throttling" up

    running = True
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
        load_coeff = THROTTLE_LOAD_COEFF if throttling else BASE_LOAD_COEFF
        load_torque = load_coeff * crank.rpm
        frame_dt = clock.get_time() / 1000.0 or (1 / FPS)
        net_torque = crank.run_frame(frame_dt, SUBSTEPS, load_torque=load_torque)

        # --- 3. Draw ---
        screen.fill((20, 20, 20))
        rpm_text = font.render(f"RPM: {crank.rpm:7.1f}", True, (255, 255, 255))
        torque_text = font.render(f"Torque: {net_torque:7.1f} N*m", True, (200, 200, 200))
        hint_text = font.render("Hold UP/W to throttle, ESC to quit", True, (120, 120, 120))
        screen.blit(rpm_text, (20, 40))
        screen.blit(torque_text, (20, 80))
        screen.blit(hint_text, (20, 160))
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
