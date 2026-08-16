import pygame
import sys

pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRACK")

clock = pygame.time.Clock()

running = True

while running: # Game Loop
# Input -> Status update -> Rending -> next Frame
## Input -> Rending -> Input -> Rending (Loop)
### Input -> Move -> Aim -> Deal -> Calculate -> Rendering


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 20, 20))

    pygame.display.flip()

    clock.tick(60)  # Max 60 FPS

pygame.quit()
sys.exit()