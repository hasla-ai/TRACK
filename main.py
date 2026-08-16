import pygame
import sys
import math

pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRACK")



clock = pygame.time.Clock()

def project_point(x, y, z, camera_x, camera_y, camera_z):

    focal_length = 500

     # 1. 카메라 기준 상대 위치
    relative_x = x - camera_x
    relative_y = y - camera_y
    relative_z = z - camera_z

    if relative_z <= 0.1:
        return None

    # 4. Perspective Projection
    screen_x = WIDTH / 2 + (relative_x / relative_z) * focal_length
    screen_y = HEIGHT / 2 - (relative_y / relative_z) * focal_length

    return int(screen_x), int(screen_y)

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

camera_x = 0.0
camera_y = 0.0
camera_z = 0.0
camera_yaw = 0.0

running = True
test_points = [
    (-3.0, 0.0, 8.0),
    (-1.0, 1.0, 6.0),
    (0.0, 0.0, 10.0),
    (2.0, 1.0, 7.0),
    (4.0, 0.0, 12.0),
]
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

    for point in test_points:

        projected = project_point(
            point[0],
            point[1],
            point[2],
            camera_x,
            camera_y,
            camera_z,
        )

        if projected is not None:
            
            pygame.draw.circle(
                screen,
                (255, 0, 0),
                projected,
                10
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