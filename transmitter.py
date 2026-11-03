"""
Transmitter: shows a static picture full-screen and changes its alpha (transparency)
over a black background using BFSK.
"""
import sys
import time
import pygame
from bfsk import *

image_path = sys.argv[1]

bits = PREAMBLE + text_to_bits(MESSAGE)
packet_time = LEAD_TIME + len(bits) * BIT_TIME
print(f"Sending '{MESSAGE}' as {len(bits)} bits, {1 / BIT_TIME:.1f} bits/s, "
      f"delta alpha = {DELTA_ALPHA}")

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = screen.get_size()
img = pygame.transform.scale(pygame.image.load(image_path).convert(), (W, H))
clock = pygame.time.Clock()

t0 = time.perf_counter()
running = True
while running:
    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            running = False

    t = (time.perf_counter() - t0) % packet_time
    if t < LEAD_TIME:
        alpha = 1.0
    else:
        alpha = 1.0 - DELTA_ALPHA * (1 - level(bits, t - LEAD_TIME))

    screen.fill((0, 0, 0))
    img.set_alpha(int(255 * alpha))
    screen.blit(img, (0, 0))
    pygame.display.flip()
    clock.tick(120)

pygame.quit()
