import pygame
import sys

pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRACK")

clock = pygame.time.Clock()

player_x = WIDTH // 2
player_y = HEIGHT // 2

player_width = 50
player_height = 50

player_speed = 300

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player_y -= player_speed / 60

    if keys[pygame.K_s]:
        player_y += player_speed / 60

    if keys[pygame.K_a]:
        player_x -= player_speed / 60

    if keys[pygame.K_d]:
        player_x += player_speed / 60

    screen.fill((20, 20, 20))

    player = pygame.Rect(
        int(player_x),
        int(player_y),
        player_width,
        player_height
    )

    pygame.draw.rect(screen, (255, 255, 255), player)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()