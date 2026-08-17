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

def clip_polygon_near_plane(polygon, near_z=0.1):

    clipped = []

    for i in range(len(polygon)):

        current = polygon[i]
        previous = polygon[i - 1]

        current_inside = current[2] >= near_z
        previous_inside = previous[2] >= near_z

        if current_inside and previous_inside:

            clipped.append(current)

        elif previous_inside and not current_inside:

            t = (near_z - previous[2]) / (current[2] - previous[2])

            intersection = (
                previous[0] + t * (current[0] - previous[0]),
                previous[1] + t * (current[1] - previous[1]),
                near_z
            )

            clipped.append(intersection)

        elif not previous_inside and current_inside:

            t = (near_z - previous[2]) / (current[2] - previous[2])

            intersection = (
                previous[0] + t * (current[0] - previous[0]),
                previous[1] + t * (current[1] - previous[1]),
                near_z
            )

            clipped.append(intersection)
            clipped.append(current)

    return clipped

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

player_vertical_velocity = 0.0
gravity = 0.8
jump_power = 12.0

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

cube_faces = [
    (0, 3, 2, 1),    # front  -Z
    (4, 5, 6, 7),    # back   +Z
    (0, 1, 5, 4),    # bottom -Y
    (3, 7, 6, 2),    # top    +Y
    (0, 4, 7, 3),    # left   -X
    (1, 2, 6, 5),    # right  +X
]

face_colors = [
    (255, 0, 0),      # 0: Red
    (0, 255, 0),      # 1: Green
    (0, 0, 255),      # 2: Blue
    (255, 255, 0),    # 3: Yellow
    (255, 0, 255),    # 4: Magenta
    (0, 255, 255),    # 5: Cyan
]

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_vertical_velocity = jump_power

    keys = pygame.key.get_pressed()

    yaw_radians = math.radians(player_yaw)

    forward_x = math.sin(yaw_radians)
    forward_z = math.cos(yaw_radians)

    right_x = math.cos(yaw_radians)
    right_z = -math.sin(yaw_radians)

    player_vertical_velocity -= gravity
    player_y += player_vertical_velocity

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

    if player_y < 0:
        player_y = 0
        player_vertical_velocity = 0

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

    camera_faces = []

    for face in cube_faces:

        camera_face = []

        for vertex_index in face:
            camera_face.append(
                camera_vertices[vertex_index]
            )

        camera_faces.append(camera_face)

    def is_front_face(face):

        if len(face) < 3:
            return False

        a = face[0]
        b = face[1]
        c = face[2]

        ab = (
            b[0] - a[0],
            b[1] - a[1],
            b[2] - a[2]
        )

        ac = (
            c[0] - a[0],
            c[1] - a[1],
            c[2] - a[2]
        )

        normal = (
            ab[1] * ac[2] - ab[2] * ac[1],
            ab[2] * ac[0] - ab[0] * ac[2],
            ab[0] * ac[1] - ab[1] * ac[0]
        )

        dot = normal[0] * (-a[0]) + \
            normal[1] * (-a[1]) + \
            normal[2] * (-a[2])

        return dot > 0

    for face_index, face in enumerate(camera_faces):
       
        if not is_front_face(face):
            continue

        clipped_face = clip_polygon_near_plane(face)

        screen_face = []

        for point in clipped_face:

            projected = camera_to_screen(
                point[0],
                point[1],
                point[2]
            )

            if projected is not None:
                screen_face.append(projected)

        if len(screen_face) >= 3:

            pygame.draw.polygon(
                screen,
                face_colors[face_index],
                screen_face
            )


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