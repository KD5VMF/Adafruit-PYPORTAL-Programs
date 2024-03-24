import board
import displayio
from adafruit_display_shapes.line import Line
import math
import time

# Initialize the display
display = board.DISPLAY
root_group = displayio.Group()
display.show(root_group)

# Parameters for the cube
cube_size = 50
cube_center = (160, 120)  # Center of the display for PyPortal

# Generate initial vertices of the cube (at origin, will translate to cube_center)
half_size = cube_size // 2
vertices = [
    [-half_size, -half_size, -half_size],
    [half_size, -half_size, -half_size],
    [half_size, half_size, -half_size],
    [-half_size, half_size, -half_size],
    [-half_size, -half_size, half_size],
    [half_size, -half_size, half_size],
    [half_size, half_size, half_size],
    [-half_size, half_size, half_size],
]

# Edges defined by vertex indices
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

def rotate_vertex(vertex, angle_y, angle_z):
    # Rotate around Y axis
    x, y, z = vertex
    temp_x = x * math.cos(angle_y) - z * math.sin(angle_y)
    temp_z = x * math.sin(angle_y) + z * math.cos(angle_y)
    # Rotate around Z axis
    z = temp_z
    x = temp_x * math.cos(angle_z) - y * math.sin(angle_z)
    y = temp_x * math.sin(angle_z) + y * math.cos(angle_z)
    return [x, y, z]

def project_vertex(vertex):
    # Project the 3D vertex onto the 2D plane
    x, y, _ = vertex
    return int(x + cube_center[0]), int(y + cube_center[1])

def draw_cube(angle_y, angle_z):
    # Clear previous frame
    while len(root_group) > 0:
        root_group.pop()

    # Rotate, project, and draw edges
    for edge in edges:
        start = vertices[edge[0]]
        end = vertices[edge[1]]
        rotated_start = rotate_vertex(start, angle_y, angle_z)
        rotated_end = rotate_vertex(end, angle_y, angle_z)
        projected_start = project_vertex(rotated_start)
        projected_end = project_vertex(rotated_end)
        line = Line(projected_start[0], projected_start[1], projected_end[0], projected_end[1], color=0xFFFFFF)
        root_group.append(line)

angle_y = 0
angle_z = 0
while True:
    draw_cube(angle_y, angle_z)
    angle_y += math.radians(5)
    angle_z += math.radians(3)
    time.sleep(0.1)
