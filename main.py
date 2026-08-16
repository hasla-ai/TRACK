import pygame
import sys

pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRACK")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)   
player_x = WIDTH // 2
player_y = HEIGHT // 2

player_width = 50
player_height = 50

player_speed = 300

mouse_sensitivity = 0.2
camera_angle = 0

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

    mouse_x, mouse_y = pygame.mouse.get_rel()

    camera_angle += mouse_x * mouse_sensitivity

    screen.fill((20, 20, 20))

    player = pygame.Rect(
        int(player_x),
        int(player_y),
        player_width,
        player_height
    )

    pygame.draw.rect(screen, (255, 255, 255), player)

    angle_text = font.render(
    f"Camera Angle: {camera_angle:.1f}",
    True,
    (255, 255, 255)
)

    screen.blit(angle_text, (20, 20))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()