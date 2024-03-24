import time
import board
import random
import displayio
from adafruit_display_shapes.circle import Circle
import math
import adafruit_touchscreen

"""
Title: Neon Bouncing Balls Simulation with Touch Interaction

About: This program simulates bouncing balls on a PyPortal display. Each ball changes its neon color 
and grows in size after hitting walls or other balls, then stays at maximum size for a duration before 
shrinking to a minimum size. Users can interact with the balls using touch input to change their 
direction and speed. The simulation runs on the Adafruit PyPortal which supports CircuitPython and 
has a touchscreen display.

Author: [Your Name]
Date: [Date of Modification]
"""

# Display Settings
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240

# Ball Settings
NUM_BALLS = 8
BALL_SPEED = 10
BALL_SIZE = 1
BALL_GROWTH = 1
MAX_BALL_SIZE = 17
MIN_BALL_SIZE = 1
MAX_SIZE_DURATION = 5  # Time in seconds to stay at max size
MIN_SIZE_DURATION = 5  # Time in seconds to stay at min size

# Neon Colors
NEON_COLORS = [
    0xFF00FF, 0x00FFFF, 0x00FF00, 0xFFFF00, 0xFF0000,
    0xFF007F, 0x7FFF00, 0x00FF7F, 0x7F00FF, 0xFF7F00,
    0x7F7FFF, 0xFF007F, 0x7FFFFF, 0x7FFF7F, 0xFF7F7F,
    0x7F0000, 0x007F00, 0x00007F, 0x7F007F, 0x007F7F,
    0x7F7F00, 0x007FFF, 0xFF7FFF, 0x7FFF7F, 0xFFFF7F
]

# Setup Touchscreen
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(DISPLAY_WIDTH, DISPLAY_HEIGHT))

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
        x, y, z = point
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
        check_for_touch(balls)

        for ball in balls:
            ball.update()
            for other in balls:
                if ball != other and check_collision(ball, other):
                    ball.velocity, other.velocity = other.velocity, ball.velocity
                    ball.adjust_for_collision(other)
                    other.adjust_for_collision(ball)

        display.refresh()
        time.sleep(0.01)

if __name__ == "__main__":
    main()
