import pygame
import sys
import math

pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRACK")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)   
player_x = 0.0
player_y = 0.0
player_z = 0.0

player_yaw = 0.0
player_pitch = 0.0

player_width = 50
player_height = 50

player_speed = 300

mouse_sensitivity = 0.2

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    yaw_radians = math.radians(player_yaw)

    forward_x = math.cos(yaw_radians)
    forward_z = math.sin(yaw_radians)

    right_x = -math.sin(yaw_radians)
    right_z = math.cos(yaw_radians)

    dt = clock.tick(60) / 1000

    if keys[pygame.K_w]:
        player_x += forward_x * player_speed * dt
        player_z += forward_z * player_speed * dt

    if keys[pygame.K_s]:
        player_x -= forward_x * player_speed * dt
        player_z -= forward_z * player_speed * dt

    if keys[pygame.K_d]:
        player_x += right_x * player_speed * dt
        player_z += right_z * player_speed * dt

    if keys[pygame.K_a]:
        player_x -= right_x * player_speed * dt
        player_z -= right_z * player_speed * dt

    mouse_x, mouse_y = pygame.mouse.get_rel()
    player_pitch = max(-89.0, min(89.0, player_pitch))

    player_yaw += mouse_x * mouse_sensitivity
    player_pitch -= mouse_y * mouse_sensitivity

    screen.fill((20, 20, 20))

    player = pygame.Rect(
        int(player_x),
        int(player_y),
        player_width,
        player_height
    )

    pygame.draw.rect(screen, (255, 255, 255), player)

    position_text = font.render(
    f"Position: ({player_x:.1f}, {player_y:.1f}, {player_z:.1f})",
    True,
    (255, 255, 255)
)

    rotation_text = font.render(
    f"Yaw: {player_yaw:.1f}  Pitch: {player_pitch:.1f}",
    True,
    (255, 255, 255)
)

    screen.blit(position_text, (20, 20))
    screen.blit(rotation_text, (20, 55))

    pygame.display.flip()


pygame.quit()
sys.exit()