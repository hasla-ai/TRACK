import pygame
import sys
import math

pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRACK")

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))


clock = pygame.time.Clock()

def clip_line_near_plane(point_a, point_b, near_z=0.1):

    ax, ay, az = point_a
    bx, by, bz = point_b

    a_inside = az >= near_z
    b_inside = bz >= near_z

    if a_inside and b_inside:
        return point_a, point_b

    if not a_inside and not b_inside:
        return None

    t = (near_z - az) / (bz - az)

    intersection = (
        ax + t * (bx - ax),
        ay + t * (by - ay),
        near_z
    )

    if a_inside:
        return point_a, intersection
    else:
        return intersection, point_b

def world_to_camera(x, y, z, camera_x, camera_y, camera_z, camera_yaw, camera_pitch):

    relative_x = x - camera_x
    relative_y = y - camera_y
    relative_z = z - camera_z

    yaw_radians = math.radians(camera_yaw)

    rotated_x = (
        relative_x * math.cos(yaw_radians)
        - relative_z * math.sin(yaw_radians)
    )

    rotated_z = (
        relative_x * math.sin(yaw_radians)
        + relative_z * math.cos(yaw_radians)
    )

    pitch_radians = math.radians(-camera_pitch)

    rotated_y = (
        relative_y * math.cos(pitch_radians)
        + rotated_z * math.sin(pitch_radians)
    )

    final_z = (
        -relative_y * math.sin(pitch_radians)
        + rotated_z * math.cos(pitch_radians)
    )

    return rotated_x, rotated_y, final_z

def camera_to_screen(x, y, z):

    focal_length = 500

    if z <= 0.1:
        return None

    screen_x = WIDTH / 2 + (x / z) * focal_length
    screen_y = HEIGHT / 2 - (y / z) * focal_length

    return int(screen_x), int(screen_y)

def project_point(x, y, z, camera_x, camera_y, camera_z, camera_yaw, camera_pitch):
    camera_point = world_to_camera(
        x, y, z,
        camera_x, camera_y, camera_z,
        camera_yaw, camera_pitch
    )

    return camera_to_screen(
        camera_point[0],
        camera_point[1],
        camera_point[2]
    )
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

cube_vertices = [
    (-100, -100, 1000),
    ( 100, -100, 1000),
    ( 100,  100, 1000),
    (-100,  100, 1000),

    (-100, -100, 1200),
    ( 100, -100, 1200),
    ( 100,  100, 1200),
    (-100,  100, 1200),
]

cube_edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),

    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),

    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    yaw_radians = math.radians(player_yaw)

    forward_x = math.sin(yaw_radians)
    forward_z = math.cos(yaw_radians)

    right_x = math.cos(yaw_radians)
    right_z = -math.sin(yaw_radians)

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


    camera_x = player_x
    camera_y = player_y
    camera_z = player_z

    mouse_x, mouse_y = pygame.mouse.get_rel()

    player_pitch = max(-89.0, min(89.0, player_pitch))

    player_yaw += mouse_x * mouse_sensitivity
    player_pitch -= mouse_y * mouse_sensitivity

    pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))

    screen.fill((20, 20, 20))

#    player = pygame.Rect(
#        int(player_x),
#        int(player_y),
#        player_width,
#        player_height
#    )

    camera_vertices = []

    for vertex in cube_vertices:

        camera_point = world_to_camera(
            vertex[0],
            vertex[1],
            vertex[2],
            camera_x,
            camera_y,
            camera_z,
            player_yaw,
            player_pitch
        )

        camera_vertices.append(camera_point)

    for edge in cube_edges:
        point_a = camera_vertices[edge[0]]
        point_b = camera_vertices[edge[1]]

        clipped_edge = clip_line_near_plane(
            point_a,
            point_b
        )

        if clipped_edge is None:
            continue

        clipped_a = camera_to_screen(
            clipped_edge[0][0],
            clipped_edge[0][1],
            clipped_edge[0][2]
        )

        clipped_b = camera_to_screen(
            clipped_edge[1][0],
            clipped_edge[1][1],
            clipped_edge[1][2]
        )

        if clipped_a is not None and clipped_b is not None:

            pygame.draw.line(
                screen,
                (255, 255, 255),
                clipped_a,
                clipped_b,
                2
            )

#    pygame.draw.rect(screen, (255, 255, 255), player)
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