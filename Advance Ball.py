import time
import board
import random
import displayio
from adafruit_display_shapes.circle import Circle
import math

# ---------------------------------
# Program Description and Parameters
# ---------------------------------
# This program creates a simulation of bouncing balls on a display. Each ball is given
# a unique neon color and will bounce off the walls and other balls.

# Display Settings
DISPLAY_WIDTH = 320  # Width of the display
DISPLAY_HEIGHT = 240  # Height of the display

# Ball Settings
NUM_BALLS = 5 # Total number of balls in the simulation
BALL_SPEED = 5  # Speed of the balls
BALL_SIZE = 20 # Diameter of the balls

# Neon Colors
# A list of 25 distinct neon color hex codes.
NEON_COLORS = [
    0xFF00FF, 0x00FFFF, 0x00FF00, 0xFFFF00, 0xFF0000,
    0xFF007F, 0x7FFF00, 0x00FF7F, 0x7F00FF, 0xFF7F00,
    0x7F7FFF, 0xFF007F, 0x7FFFFF, 0x7FFF7F, 0xFF7F7F,
    0x7F0000, 0x007F00, 0x00007F, 0x7F007F, 0x007F7F,
    0x7F7F00, 0x007FFF, 0xFF7FFF, 0x7FFF7F, 0xFFFF7F
]

# -------------------
# Ball Class Definition
# -------------------
class Ball:
    # Initializer for the Ball class
    def __init__(self, group, color, pos, velocity, size):
        self.size = size
        self.group = group
        self.color = color
        self.position = pos
        self.velocity = velocity
        self.circle = Circle(pos[0], pos[1], size // 2, fill=color)
        self.group.append(self.circle)

    # Update the position of the ball and handle wall collisions
    def update(self):
        x, y = self.position
        vx, vy = self.velocity

        # Update position
        x += vx
        y += vy

        # Bounce off the edges and adjust position to be within bounds
        if x < 0 or x > DISPLAY_WIDTH - self.size:
            vx = -vx
            x = max(0, min(x, DISPLAY_WIDTH - self.size))
        if y < 0 or y > DISPLAY_HEIGHT - self.size:
            vy = -vy
            y = max(0, min(y, DISPLAY_HEIGHT - self.size))

        self.position = (x, y)
        self.velocity = (vx, vy)
        self.circle.x = int(x)
        self.circle.y = int(y)

    # Adjust position to prevent balls from sticking after a collision
    def adjust_for_collision(self, other):
        dx = other.position[0] - self.position[0]
        dy = other.position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        overlap = self.size / 2 + other.size / 2 - distance
        if distance != 0:
            self.position = (self.position[0] - overlap * dx / distance, self.position[1] - overlap * dy / distance)

# ------------------------
# Collision Check Function
# ------------------------
# Checks if two balls have collided
def check_collision(ball1, ball2):
    dx = ball1.position[0] - ball2.position[0]
    dy = ball1.position[1] - ball2.position[1]
    distance = math.sqrt(dx**2 + dy**2)
    if distance < ball1.size / 2 + ball2.size / 2:
        return True
    return False

# ----------------
# Main Program Loop
# ----------------
def main():
    # Setup display
    display = board.DISPLAY
    display_group = displayio.Group()
    display.show(display_group)

    # Create balls
    balls = []
    for _ in range(NUM_BALLS):
        color_index = random.randrange(len(NEON_COLORS))
        color = NEON_COLORS.pop(color_index)  # Randomly select and remove a color
        pos = (random.randint(0, DISPLAY_WIDTH - BALL_SIZE), random.randint(0, DISPLAY_HEIGHT - BALL_SIZE))
        velocity = (random.uniform(-BALL_SPEED, BALL_SPEED), random.uniform(-BALL_SPEED, BALL_SPEED))
        ball = Ball(display_group, color, pos, velocity, BALL_SIZE)
        balls.append(ball)

    # Main loop
    while True:
        for ball in balls:
            ball.update()
            for other in balls:
                if ball != other and check_collision(ball, other):
                    # Swap velocities and adjust positions
                    ball.velocity, other.velocity = other.velocity, ball.velocity
                    ball.adjust_for_collision(other)
                    other.adjust_for_collision(ball)

        # Refresh the display
        display.refresh()
        time.sleep(0.01)

if __name__ == "__main__":
    main()
