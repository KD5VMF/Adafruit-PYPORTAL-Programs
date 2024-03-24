import time
import board
import random
import displayio
from adafruit_display_shapes.circle import Circle

# Title: Bouncing Balls Animation
# About: This program creates an animation of balls bouncing within the boundaries of a display.
#        Each ball is randomly positioned, colored, and moves at a random velocity.

class Ball:
    def __init__(self, group, color, pos, velocity, size):
        """
        Initialize a ball.
        - group: display group to which the ball belongs
        - color: color of the ball
        - pos: initial position (x, y)
        - velocity: initial velocity (vx, vy)
        - size: diameter of the ball
        """
        self.size = size
        self.group = group
        self.color = color
        self.position = pos
        self.velocity = velocity
        self.circle = Circle(pos[0], pos[1], size // 2, fill=color)
        self.group.append(self.circle)

    def update(self, display_width, display_height):
        """
        Update the ball's position and handle bouncing off the edges.
        """
        x, y = self.position
        vx, vy = self.velocity

        # Update position based on velocity
        x += vx
        y += vy

        # Bounce off the edges by reversing velocity
        if x < 0 or x > display_width - self.size:
            vx = -vx
        if y < 0 or y > display_height - self.size:
            vy = -vy

        # Update ball's position and velocity
        self.position = (x, y)
        self.velocity = (vx, vy)
        self.circle.x = int(x)
        self.circle.y = int(y)

def main():
    # Initialize parameters for the animation
    num_balls = 10
    ball_speed = 3
    ball_size = 10

    # Setup display
    display = board.DISPLAY
    display_group = displayio.Group()
    display.show(display_group)

    # Get display dimensions
    display_width = display.width
    display_height = display.height

    # Create and initialize balls
    balls = []
    for _ in range(num_balls):
        color = random.randint(0, 0xFFFFFF)
        pos = (random.randint(0, display_width - ball_size), random.randint(0, display_height - ball_size))
        velocity = (random.uniform(-ball_speed, ball_speed), random.uniform(-ball_speed, ball_speed))
        ball = Ball(display_group, color, pos, velocity, ball_size)
        balls.append(ball)

    # Animation loop
    while True:
        for ball in balls:
            ball.update(display_width, display_height)

        # Refresh the display
        display.refresh()

        # Short delay to control animation speed
        time.sleep(0.01)

if __name__ == "__main__":
    main()
