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

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other):
        return Vector3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def __mul__(self, scalar):
        return Vector3(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar
        )

    def length(self):
        return math.sqrt(
            self.x * self.x +
            self.y * self.y +
            self.z * self.z
        )
    
    def normalized(self):
        length = self.length()

        if length == 0:
            return Vector3(0, 0, 0)

        return Vector3(
            self.x / length,
            self.y / length,
            self.z / length
        )
    
    def dot(self, other):
        return (
            self.x * other.x +
            self.y * other.y +
            self.z * other.z
        )
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

class Transform:
    def __init__(self, position, rotation, scale, parent=None):
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.parent = parent

    def get_world_position(self):
        if self.parent is None:
            return self.position
        parent_position = self.parent.get_world_position()
        parent_rotation = self.parent.get_world_rotation()

        rotated_x, rotated_y, rotated_z = rotate_x(
            self.position.x,
            self.position.y,
            self.position.z,
            parent_rotation.y
        )

        return parent_position + Vector3(
            rotated_x,
            rotated_y,
            rotated_z
        )
    
    def get_world_rotation(self):
        if self.parent is None:
            return self.rotation

        return self.parent.get_world_rotation() + self.rotation

font = pygame.font.Font(None, 36)   

player_vertical_velocity = 0.0
gravity = 0.8
jump_power = 12.0

player_width = 50
player_height = 50

player_speed = 300

mouse_sensitivity = 0.2

running = True

player_transform = Transform(
    Vector3(0, 0, 0),
    Vector3(0, 0, 0),
    Vector3(1, 1, 1)
)

camera_transform = Transform(
    Vector3(0, 2, 0), # position
    Vector3(0, 0, 0), # rotation
    Vector3(1, 1, 1), # scale
    parent=player_transform # parent
)

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

def rotate_y(x, y, z, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rotated_x = x * cos_a - z * sin_a
    rotated_y = y
    rotated_z = x * sin_a + z * cos_a

    return rotated_x, rotated_y, rotated_z

def rotate_x(x, y, z, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rotated_x = x
    rotated_y = y * cos_a - z * sin_a
    rotated_z = y * sin_a + z * cos_a

    return rotated_x, rotated_y, rotated_z

def world_to_camera(x, y, z, camera_position, camera_rotation):

    relative_x = x - camera_position.x
    relative_y = y - camera_position.y
    relative_z = z - camera_position.z

    yaw_radians = math.radians(camera_rotation.y)

    rotated_x = (
        relative_x * math.cos(yaw_radians)
        - relative_z * math.sin(yaw_radians)
    )

    rotated_z = (
        relative_x * math.sin(yaw_radians)
        + relative_z * math.cos(yaw_radians)
    )

    pitch_radians = math.radians(-camera_rotation.x)

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

def project_point(x, y, z, camera_position, camera_rotation):
    camera_point = world_to_camera(
        x, y, z,
        camera_position,
        camera_rotation
    )

    return camera_to_screen(
        camera_point[0],
        camera_point[1],
        camera_point[2]
    )


cube_transform = Transform(
    Vector3(0, 0, 1000), 
    Vector3(0, 0.1, 0),
    Vector3(1, 1, 1)
)

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

    yaw_radians = math.radians(player_transform.rotation.y)

    forward_x = math.sin(yaw_radians)
    forward_z = math.cos(yaw_radians)

    right_x = math.cos(yaw_radians)
    right_z = -math.sin(yaw_radians)

    player_vertical_velocity -= gravity
    player_transform.position.y += player_vertical_velocity

    dt = clock.tick(60) / 1000

    if keys[pygame.K_w]:
        player_transform.position.x += forward_x * player_speed * dt
        player_transform.position.z += forward_z * player_speed * dt

    if keys[pygame.K_s]:
        player_transform.position.x -= forward_x * player_speed * dt
        player_transform.position.z -= forward_z * player_speed * dt

    if keys[pygame.K_d]:
        player_transform.position.x += right_x * player_speed * dt
        player_transform.position.z += right_z * player_speed * dt

    if keys[pygame.K_a]:
        player_transform.position.x -= right_x * player_speed * dt
        player_transform.position.z -= right_z * player_speed * dt

    if player_transform.position.y < 0:
        player_transform.position.y = 0
        player_vertical_velocity = 0

    camera_world_position = camera_transform.get_world_position()
    camera_world_rotation = camera_transform.get_world_rotation()

    mouse_x, mouse_y = pygame.mouse.get_rel()

    player_transform.rotation.y += mouse_x * mouse_sensitivity
    camera_transform.rotation.x -= mouse_y * mouse_sensitivity

    camera_transform.rotation.x = max(-89.0, min(89.0, camera_transform.rotation.x))
    
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

        scaled_x = vertex[0] * cube_transform.scale.x
        scaled_y = vertex[1] * cube_transform.scale.y
        scaled_z = vertex[2] * cube_transform.scale.z

        rotated = rotate_y(
            scaled_x,
            scaled_y,
            scaled_z,
            cube_transform.rotation.y
        )

        world_x = rotated[0] + cube_transform.position.x
        world_y = rotated[1] + cube_transform.position.y
        world_z = rotated[2] + cube_transform.position.z

        camera_point = world_to_camera(
            world_x,
            world_y,
            world_z,
            camera_world_position,
            camera_world_rotation
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
    f"Position: ({player_transform.position.x:.1f}, "
    f"{player_transform.position.y:.1f}, "
    f"{player_transform.position.z:.1f})",
    True,
    (255, 255, 255)
)

    rotation_text = font.render(
    f"Yaw: {player_transform.rotation.y:.1f}  Pitch: {camera_transform.rotation.x:.1f}",
    True,
    (255, 255, 255)
)

    screen.blit(position_text, (20, 20))
    screen.blit(rotation_text, (20, 55))

    pygame.display.flip()


pygame.quit()
sys.exit()