"""
Enhanced Breakout Game for Adafruit PyPortal
===========================================

This is an enhanced Breakout game developed for the Adafruit PyPortal.
The game features an AI-controlled paddle, randomized brick colors, scaled-down
game elements for better fit, and an adjustable scoreboard size.

Features:
- AI-controlled paddle that follows the ball's horizontal movement.
- Ball mechanics with collision detection against walls, paddle, and bricks.
- Brick layout with multiple rows, each brick having a random color.
- Score and lives tracking with an adjustable scoreboard size.
- Game over and victory screens.
- Adjustable paddle size and scoreboard size via variables.
- Automatic game restart with new random brick colors after victory.
- Prevents the ball from getting stuck bouncing straight up and down.

Developed by: ChatGPT with Direction from Adam Figueroa
"""

import board
import displayio
import terminalio
import time
import random
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_text import label
from adafruit_touchscreen import Touchscreen

# ---------------------------
# Game Constants
# ---------------------------

# Adjustable Paddle Sizes
PADDLE_WIDTH = 40    # Further reduced width
PADDLE_HEIGHT = 5    # Further reduced height

# Ball Settings
BALL_RADIUS = 3
INITIAL_BALL_SPEED_X = 2.0
INITIAL_BALL_SPEED_Y = -2.0
MAX_BALL_SPEED_X = 5.0
MAX_BALL_SPEED_Y = 5.0
BALL_SPEED_INCREMENT = 0.2  # Speed increase after hitting a brick
MIN_BALL_SPEED_X = 1.5      # Increased minimum horizontal speed to prevent vertical trajectory

# Brick Settings
BRICK_ROWS = 4
BRICK_COLUMNS = 6  # Further reduced columns to make the game area less wide
BRICK_WIDTH = 35
BRICK_HEIGHT = 10
BRICK_PADDING = 3
BRICK_OFFSET_TOP = 40
BRICK_OFFSET_LEFT = (board.DISPLAY.width - (BRICK_COLUMNS * (BRICK_WIDTH + BRICK_PADDING))) // 2

# Paddle Movement (AI Speed)
PADDLE_SPEED = 3.2  # Reduced speed for smoother tracking

# Scoreboard Settings
SCOREBOARD_FONT_SIZE = 1  # Further reduced scoreboard size

# Lives
INITIAL_LIVES = 3

# Colors Palette (More vibrant and diverse)
COLOR_PALETTE = [
    0xFF5733,  # Red
    0x33FF57,  # Green
    0x3357FF,  # Blue
    0xFF33A8,  # Pink
    0xFF8F33,  # Orange
    0x8F33FF,  # Purple
    0x33FFF5,  # Cyan
    0xF5FF33,  # Yellow
    0xFF33F6,  # Magenta
    0x33FFB5   # Mint
]

# Additional Colors
BALL_COLOR = 0xFFFFFF           # White
PADDLE_COLOR = 0x00FF00         # Green
SCORE_COLOR = 0xFFFFFF           # White
GAME_OVER_COLOR = 0xFF00FF      # Magenta
VICTORY_COLOR = 0xFFFF00         # Yellow

# ---------------------------
# Setup Display and Touchscreen
# ---------------------------
display = board.DISPLAY
screen = displayio.Group()
display.show(screen)

# Initialize Touchscreen (adjust the calibration values as needed)
ts = Touchscreen(board.TOUCH_XL, board.TOUCH_XR, board.TOUCH_YD, board.TOUCH_YU,
                calibration=((5200, 59000), (5800, 57000)),
                size=(display.width, display.height))

# ---------------------------
# Initialize Game Variables
# ---------------------------
score = 0
lives = INITIAL_LIVES
game_over = False
victory = False

# ---------------------------
# Create Paddle
# ---------------------------
paddle = Rect(0, 0, PADDLE_WIDTH, PADDLE_HEIGHT, fill=PADDLE_COLOR)
paddle_group = displayio.Group()
paddle_group.append(paddle)
screen.append(paddle_group)

# Position the paddle at the bottom center
paddle_group.x = (display.width - PADDLE_WIDTH) // 2
paddle_group.y = display.height - PADDLE_HEIGHT - 15  # 15 pixels from the bottom

# ---------------------------
# Create Ball
# ---------------------------
ball_pos_x = float(display.width) / 2
ball_pos_y = float(display.height) / 2
ball_velocity_x = INITIAL_BALL_SPEED_X if random.choice([True, False]) else -INITIAL_BALL_SPEED_X
ball_velocity_y = INITIAL_BALL_SPEED_Y if random.choice([True, False]) else -INITIAL_BALL_SPEED_Y

ball = Circle(int(ball_pos_x), int(ball_pos_y), BALL_RADIUS, fill=BALL_COLOR)
screen.append(ball)

# ---------------------------
# Create Bricks
# ---------------------------
bricks = []

def setup_bricks():
    """Initializes the bricks with random colors."""
    global bricks
    bricks = []
    for row in range(BRICK_ROWS):
        brick_row = []
        for col in range(BRICK_COLUMNS):
            brick_color = random.choice(COLOR_PALETTE)
            brick = Rect(0, 0, BRICK_WIDTH, BRICK_HEIGHT, fill=brick_color)
            brick_group = displayio.Group()
            brick_group.append(brick)
            brick_x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
            brick_y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
            brick_group.x = brick_x
            brick_group.y = brick_y
            screen.append(brick_group)
            brick_row.append(brick_group)
        bricks.append(brick_row)

# Initialize bricks
setup_bricks()

# ---------------------------
# Create Scoreboard
# ---------------------------
score_label = label.Label(
    terminalio.FONT,
    text=f"Score: {score}  Lives: {lives}",
    color=SCORE_COLOR,
    x=10,
    y=10,
    scale=SCOREBOARD_FONT_SIZE
)
screen.append(score_label)

# ---------------------------
# Helper Functions
# ---------------------------
def reset_ball():
    """Resets the ball to the center with initial speed."""
    global ball_pos_x, ball_pos_y, ball_velocity_x, ball_velocity_y, game_over, victory
    ball_pos_x = float(display.width) / 2
    ball_pos_y = float(display.height) / 2
    ball.x = int(ball_pos_x)
    ball.y = int(ball_pos_y)
    # Ensure ball has sufficient horizontal speed
    ball_velocity_x = INITIAL_BALL_SPEED_X * random.choice([-1, 1])
    ball_velocity_y = INITIAL_BALL_SPEED_Y * random.choice([-1, 1])
    # Prevent the ball from starting with too vertical a trajectory
    if abs(ball_velocity_x) < MIN_BALL_SPEED_X:
        ball_velocity_x = MIN_BALL_SPEED_X * random.choice([-1, 1])
    game_over = False
    victory = False

def update_scoreboard():
    """Updates the scoreboard text."""
    score_label.text = f"Score: {score}  Lives: {lives}"

def display_game_over():
    """Displays the Game Over screen and resets the game."""
    global game_over
    game_over = True
    game_over_label = label.Label(
        terminalio.FONT,
        text="GAME OVER",
        color=GAME_OVER_COLOR,
        x=(display.width - len("GAME OVER") * 6) // 2,
        y=display.height // 2 - 10,
        scale=3
    )
    screen.append(game_over_label)
    time.sleep(3)
    screen.remove(game_over_label)
    reset_ball()
    setup_bricks()
    update_scoreboard()

def display_victory():
    """Displays the Victory screen and resets the game with new brick colors."""
    global victory
    victory = True
    victory_label = label.Label(
        terminalio.FONT,
        text="VICTORY!",
        color=VICTORY_COLOR,
        x=(display.width - len("VICTORY!") * 6) // 2,
        y=display.height // 2 - 10,
        scale=3
    )
    screen.append(victory_label)
    time.sleep(3)
    screen.remove(victory_label)
    reset_ball()
    setup_bricks()  # Reset bricks with new random colors
    update_scoreboard()

def is_ball_colliding_with_paddle(ball_x, ball_y, paddle_group):
    """Determines if the ball is colliding with the paddle."""
    paddle_x = paddle_group.x
    paddle_y = paddle_group.y
    # Paddle boundaries
    paddle_left = paddle_x
    paddle_right = paddle_x + PADDLE_WIDTH
    paddle_top = paddle_y
    paddle_bottom = paddle_y + PADDLE_HEIGHT
    
    # Check collision with the paddle's rectangle
    if (paddle_left <= ball_x <= paddle_right) and (paddle_top <= ball_y + BALL_RADIUS >= paddle_bottom):
        return True
    
    return False

# ---------------------------
# Main Game Loop
# ---------------------------
while True:
    if not game_over and not victory:
        # AI-Controlled Paddle Movement
        desired_paddle_x = ball_pos_x - (PADDLE_WIDTH / 2)
        # Clamp desired position within screen boundaries
        desired_paddle_x = max(0, min(desired_paddle_x, display.width - PADDLE_WIDTH))
        current_paddle_x = float(paddle_group.x)
        # Move paddle towards desired position
        if current_paddle_x < desired_paddle_x:
            current_paddle_x += PADDLE_SPEED
        elif current_paddle_x > desired_paddle_x:
            current_paddle_x -= PADDLE_SPEED
        # Clamp the paddle's position
        current_paddle_x = max(0, min(current_paddle_x, display.width - PADDLE_WIDTH))
        paddle_group.x = int(current_paddle_x)
        
        # Move the ball
        ball_pos_x += ball_velocity_x
        ball_pos_y += ball_velocity_y
        ball.x = int(ball_pos_x)
        ball.y = int(ball_pos_y)
        
        # Bounce off the left and right walls
        if ball_pos_x <= BALL_RADIUS:
            ball_velocity_x *= -1
            ball_pos_x = BALL_RADIUS  # Prevent sticking
            # Optional: Add slight randomness to avoid vertical bounces
            ball_velocity_x += random.uniform(-0.5, 0.5)
            # Ensure ball_velocity_x doesn't drop below MIN_BALL_SPEED_X
            if abs(ball_velocity_x) < MIN_BALL_SPEED_X:
                ball_velocity_x = MIN_BALL_SPEED_X * (1 if ball_velocity_x >= 0 else -1)
        elif ball_pos_x >= display.width - BALL_RADIUS:
            ball_velocity_x *= -1
            ball_pos_x = display.width - BALL_RADIUS  # Prevent sticking
            # Optional: Add slight randomness to avoid vertical bounces
            ball_velocity_x += random.uniform(-0.5, 0.5)
            # Ensure ball_velocity_x doesn't drop below MIN_BALL_SPEED_X
            if abs(ball_velocity_x) < MIN_BALL_SPEED_X:
                ball_velocity_x = MIN_BALL_SPEED_X * (1 if ball_velocity_x >= 0 else -1)
        
        # Bounce off the top wall
        if ball_pos_y <= BALL_RADIUS:
            ball_velocity_y *= -1
            ball_pos_y = BALL_RADIUS  # Prevent sticking
            # Optional: Add slight randomness to avoid vertical bounces
            ball_velocity_x += random.uniform(-0.5, 0.5)
            # Ensure ball_velocity_x doesn't drop below MIN_BALL_SPEED_X
            if abs(ball_velocity_x) < MIN_BALL_SPEED_X:
                ball_velocity_x = MIN_BALL_SPEED_X * (1 if ball_velocity_x >= 0 else -1)
        
        # Check collision with the paddle
        if is_ball_colliding_with_paddle(ball_pos_x, ball_pos_y, paddle_group):
            ball_velocity_y *= -1
            ball_pos_y = paddle_group.y - BALL_RADIUS  # Prevent sticking
            # Adjust ball velocity based on where it hit the paddle
            hit_pos = (ball_pos_x - paddle_group.x) / PADDLE_WIDTH  # 0 (left) to 1 (right)
            # Calculate new horizontal speed, ensuring minimum speed
            ball_velocity_x = (hit_pos - 0.5) * 4  # Adjust horizontal speed between -2 to +2
            # Ensure minimum horizontal speed to prevent straight vertical movement
            if 0 < ball_velocity_x < MIN_BALL_SPEED_X:
                ball_velocity_x = MIN_BALL_SPEED_X
            elif -MIN_BALL_SPEED_X < ball_velocity_x < 0:
                ball_velocity_x = -MIN_BALL_SPEED_X
            # Introduce slight randomness to avoid predictable patterns
            ball_velocity_x += random.uniform(-0.2, 0.2)
            # Cap the horizontal speed
            ball_velocity_x = max(-MAX_BALL_SPEED_X, min(ball_velocity_x, MAX_BALL_SPEED_X))
        
        # Check if the ball goes below the paddle (lose a life)
        if ball_pos_y >= display.height + BALL_RADIUS:
            lives -= 1
            update_scoreboard()
            if lives <= 0:
                display_game_over()
            else:
                reset_ball()
            time.sleep(1)
            continue  # Skip the rest and restart the loop
        
        # Check collision with bricks
        brick_hit = False
        for row in bricks:
            for brick_group in row:
                brick = brick_group[0]  # Assuming the first element is the Rect
                # Brick boundaries
                brick_left = brick_group.x
                brick_right = brick_group.x + BRICK_WIDTH
                brick_top = brick_group.y
                brick_bottom = brick_group.y + BRICK_HEIGHT
                # Check collision
                if (brick_left <= ball_pos_x <= brick_right) and (brick_top <= ball_pos_y <= brick_bottom):
                    # Collision detected
                    ball_velocity_y *= -1
                    if ball_velocity_y > 0:
                        ball_pos_y = brick_bottom + BALL_RADIUS
                    else:
                        ball_pos_y = brick_top - BALL_RADIUS
                    # Remove the brick
                    screen.remove(brick_group)
                    row.remove(brick_group)
                    score += 10
                    update_scoreboard()
                    # Increase ball speed dynamically with capping
                    if abs(ball_velocity_x) < MAX_BALL_SPEED_X:
                        ball_velocity_x += BALL_SPEED_INCREMENT if ball_velocity_x > 0 else -BALL_SPEED_INCREMENT
                        ball_velocity_x = max(-MAX_BALL_SPEED_X, min(ball_velocity_x, MAX_BALL_SPEED_X))
                    if abs(ball_velocity_y) < MAX_BALL_SPEED_Y:
                        ball_velocity_y += BALL_SPEED_INCREMENT if ball_velocity_y > 0 else -BALL_SPEED_INCREMENT
                        ball_velocity_y = max(-MAX_BALL_SPEED_Y, min(ball_velocity_y, MAX_BALL_SPEED_Y))
                    brick_hit = True
                    # Prevent vertical loops by ensuring horizontal speed
                    if abs(ball_velocity_x) < MIN_BALL_SPEED_X:
                        ball_velocity_x = MIN_BALL_SPEED_X * (1 if ball_velocity_x >= 0 else -1)
                    # Introduce slight randomness to avoid predictable patterns
                    ball_velocity_x += random.uniform(-0.2, 0.2)
                    # Cap the horizontal speed
                    ball_velocity_x = max(-MAX_BALL_SPEED_X, min(ball_velocity_x, MAX_BALL_SPEED_X))
                    break  # Exit the loop after collision
            if brick_hit:
                break  # Exit the outer loop if a brick was hit
        
        # Check for victory (all bricks destroyed)
        bricks_remaining = any(bricks)
        if not bricks_remaining:
            display_victory()
    
    # Update the display
    display.refresh(minimum_frames_per_second=0)
    
    # Small delay to control game speed
    time.sleep(0.01)  # Approximately 100 FPS
