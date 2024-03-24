import time
import board
import random
import displayio
from adafruit_display_shapes.circle import Circle
import math
import adafruit_touchscreen

"""
Title: Neon Bouncing Balls Simulation with Enhanced Color Variety

About: This enhanced program simulates bouncing balls on a PyPortal display, each changing its color randomly 
from a set of 125 bright neon shades. The balls grow in size after hitting walls or other balls, then stay at 
maximum size for a duration before shrinking to a minimum size. Users can interact with the balls using touch 
input to change their direction and speed. The simulation, running on the Adafruit PyPortal, showcases the 
capabilities of CircuitPython with a touchscreen display and vibrant graphics.

"""

# Display Settings
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240

# Ball Settings
NUM_BALLS = 7
BALL_SPEED = 7
BALL_SIZE = 1
BALL_GROWTH = 1
MAX_BALL_SIZE = 17
MIN_BALL_SIZE = 1
MAX_SIZE_DURATION = 7  # Time in seconds to stay at max size
MIN_SIZE_DURATION = 7  # Time in seconds to stay at min size

# Expanded Neon Colors with a total of 125 bright neon shades
NEON_COLORS = [
    0xD500FF, 0x00FFEA, 0x00FF00, 0xFFFF00, 0xFF0000,
    0xFF00FF, 0xB2FF59, 0x18FFFF, 0xF50057, 0xFF6D00,
    0x651FFF, 0xFF1744, 0x00BFA5, 0xC51162, 0x304FFE,
    0x6200EA, 0x0091EA, 0x00C853, 0x64DD17, 0xAEEA00,
    0xFFD600, 0xFFAB00, 0xFF6D00, 0xDD2C00, 0x3E2723,
    0x1DE9B6, 0x00B0FF, 0x2979FF, 0x3D5AFE, 0x6200EA,
    0x7C4DFF, 0x8C9EFF, 0xB388FF, 0x8C9EFF, 0x82B1FF,
    0x448AFF, 0x2979FF, 0x2962FF, 0x536DFE, 0x3D5AFE,
    0x7C4DFF, 0x651FFF, 0x6200EA, 0x8E24AA, 0x5E35B1,
    0x512DA8, 0x673AB7, 0x9575CD, 0xB39DDB, 0x7E57C2,
    0x673AB7, 0x5E35B1, 0x512DA8, 0xD81B60, 0xC2185B,
    0xAD1457, 0xE91E63, 0xEC407A, 0xFF80AB, 0xFF4081,
    0xF50057, 0xC51162, 0xF8BBD0, 0xF48FB1, 0xF06292,
    0xEC407A, 0xE91E63, 0xD81B60, 0xC2185B, 0x880E4F,
    0xFF5252, 0xFF1744, 0xD50000, 0xF44336, 0xE57373,
    0xEF5350, 0xE53935, 0xD32F2F, 0xC62828, 0xB71C1C,
    0xFF8A80, 0xFF5252, 0xFF1744, 0xD50000, 0xFF5722,
    0xFF7043, 0xFF8A65, 0xFFAB91, 0xF4511E, 0xE64A19,
    0xD84315, 0xBF360C, 0xFF9E80, 0xFF6E40, 0xFF3D00,
    0xDD2C00, 0xFFC107, 0xFFB300, 0xFFA000, 0xFF8F00,
    0xFF6F00, 0xFFE57F, 0xFFD740, 0xFFC400, 0xFFAB00,
    0xFFD180, 0xFFAB40, 0xFF9100, 0xFF6D00, 0xF57F17,
    0xF9A825, 0xFBC02D, 0xFDD835, 0xFBC02D, 0xF9A825,
    0xF57F17, 0xFFFF8D, 0xFFFF00, 0xFFEA00, 0xFFD600,
    # Add more specific neon colors as needed
]

## Setup Touchscreen
ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL, board.TOUCH_XR, board.TOUCH_YD, board.TOUCH_YU,
    calibration=((0, 65535), (0, 65535)),
    size=(DISPLAY_WIDTH, DISPLAY_HEIGHT)
)

# Ball Class
class Ball:
    def __init__(self, group, color, pos, velocity, size):
        self.size = size
        self.group = group
        self.color = color
        self.position = pos
        self.velocity = velocity
        self.circle = Circle(pos[0], pos[1], size // 2, fill=color)
        self.group.append(self.circle)
        self.hit_count = 0
        self.state = "growing"
        self.state_change_time = time.monotonic()

    def update(self):
        x, y = self.position
        vx, vy = self.velocity

        # Update position and check for wall collisions
        x += vx
        y += vy
        collision_occurred = False

        if x < 0 or x > DISPLAY_WIDTH - self.size:
            vx = -vx
            x = max(0, min(x, DISPLAY_WIDTH - self.size))
            collision_occurred = True
        if y < 0 or y > DISPLAY_HEIGHT - self.size:
            vy = -vy
            y = max(0, min(y, DISPLAY_HEIGHT - self.size))
            collision_occurred = True

        if collision_occurred:
            self.hit_count += 1
            if self.hit_count >= 5:
                self.change_color()
            self.grow()

        self.position = (x, y)
        self.velocity = (vx, vy)
        self.circle.x = int(x)
        self.circle.y = int(y)

        # State change logic
        current_time = time.monotonic()
        if self.state == "at_max_size" and current_time - self.state_change_time > MAX_SIZE_DURATION:
            self.state = "shrinking"
            self.state_change_time = current_time
        elif self.state == "at_min_size" and current_time - self.state_change_time > MIN_SIZE_DURATION:
            self.state = "growing"
            self.state_change_time = current_time

    def grow(self):
        if self.state == "growing":
            if self.size < MAX_BALL_SIZE:
                self.size += BALL_GROWTH
                self.update_circle()
            else:
                self.state = "at_max_size"
                self.state_change_time = time.monotonic()
        elif self.state == "shrinking":
            if self.size > MIN_BALL_SIZE:
                self.size -= BALL_GROWTH
                self.update_circle()
            else:
                self.state = "at_min_size"
                self.state_change_time = time.monotonic()

    def update_circle(self):
        self.group.remove(self.circle)
        self.circle = Circle(int(self.position[0]), int(self.position[1]), self.size // 2, fill=self.color)
        self.group.append(self.circle)

    def change_color(self):
        new_color_index = random.randrange(len(NEON_COLORS))
        new_color = NEON_COLORS[new_color_index]
        self.color = new_color
        self.circle.fill = new_color
        self.hit_count = 0

    def redirect(self, new_velocity):
        self.velocity = new_velocity

    def adjust_for_collision(self, other):
        dx = other.position[0] - self.position[0]
        dy = other.position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        min_distance = self.size / 2 + other.size / 2
        if distance < min_distance:
            overlap = min_distance - distance
            if distance != 0:
                adjust_x = overlap * dx / distance
                adjust_y = overlap * dy / distance
                self.position = (self.position[0] - adjust_x / 2, self.position[1] - adjust_y / 2)
                other.position = (other.position[0] + adjust_x / 2, other.position[1] + adjust_y / 2)

def check_collision(ball1, ball2):
    dx = ball1.position[0] - ball2.position[0]
    dy = ball1.position[1] - ball2.position[1]
    distance = math.sqrt(dx**2 + dy**2)
    return distance < ball1.size / 2 + ball2.size / 2

def check_for_touch(balls):
    point = ts.touch_point
    if point:
        x, y, _ = point  # The z value is the pressure, which we don't need here
        for ball in balls:
            if math.sqrt((ball.position[0] - x)**2 + (ball.position[1] - y)**2) <= ball.size / 2:
                ball.redirect((-ball.velocity[0], -ball.velocity[1]))
                break

def main():
    display = board.DISPLAY
    display_group = displayio.Group()
    display.show(display_group)

    balls = []
    for _ in range(NUM_BALLS):
        color_index = random.randrange(len(NEON_COLORS))
        color = NEON_COLORS[color_index]
        pos = (random.randint(0, DISPLAY_WIDTH - BALL_SIZE), random.randint(0, DISPLAY_HEIGHT - BALL_SIZE))
        velocity = (random.uniform(-BALL_SPEED, BALL_SPEED), random.uniform(-BALL_SPEED, BALL_SPEED))
        ball = Ball(display_group, color, pos, velocity, BALL_SIZE)
        balls.append(ball)

    while True:
        #check_for_touch(balls)

        for ball in balls:
            ball.update()
            for other in balls:
                if ball != other and check_collision(ball, other):
                    ball.adjust_for_collision(other)
                    other.adjust_for_collision(ball)
                    # Swap velocities for a simple collision response
                    ball.velocity, other.velocity = other.velocity, ball.velocity

        display.refresh()
        time.sleep(0.01)

if __name__ == "__main__":
    main()
