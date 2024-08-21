"""
Space Invaders-Style Game for Adafruit PyPortal
===============================================

This is a simple "Space Invaders"-style game developed for the Adafruit PyPortal.
The player controls a green rectangle at the bottom of the screen that moves
automatically and shoots at the invaders. The invaders are red, blue, and yellow
rectangles that move across the screen, reverse direction when they hit the edges,
and shoot back at the player.

Gameplay:
---------
- The player must destroy all invaders to win each level.
- The player automatically moves left and right, and will dodge shots when needed.
- As the player progresses through levels, additional rows of invaders are added,
  making the game more challenging. The invaders' speed, shooting frequency, and
  intelligence also increase with each level.

Features:
---------
- Levels dynamically increase in difficulty, with more rows of invaders appearing.
- Invader rows are color-coded: red for the first row, blue for the second row,
  and yellow for the third row.
- The PyPortal's onboard NeoPixel backlight provides feedback on the game's progress:
  green if the player is winning, red if the invaders are winning, and off if the
  game is tied.
- Automatic collision detection handles hits between shots and invaders or the player.

Controls and Behavior:
----------------------
- The game runs automatically without player input. The player moves left and right
  on its own, shooting at invaders when aligned with them.
- The game resets after each round, and the player progresses to the next level with
  more invaders.

Optimized for PyPortal:
-----------------------
- The code is optimized to run smoothly on the Adafruit PyPortal by throttling
  the movement and shooting updates to prevent performance issues.
- Movement and screen updates are controlled through timed delays to ensure
  consistent behavior.

This game is designed to be easily shared and enjoyed by anyone who has an
Adafruit PyPortal. Feel free to experiment with the code and add your own features!

Developed by: Chat-GPT4o with Direction from Adam Figueroa
"""


import board
import displayio
import time
import random
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio
import neopixel  # To control the backlight

# Setup display
display = board.DISPLAY
screen = displayio.Group()

# Setup the backlight (using the onboard NeoPixel)
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixels.brightness = 1.0  # Full brightness

def update_backlight():
    if player_wins > invader_wins:
        pixels.fill((0, 255, 0))  # Green for player leading
    elif invader_wins > player_wins:
        pixels.fill((255, 0, 0))  # Red for invader leading
    else:
        pixels.fill((0, 0, 0))  # Backlight off if tied

# Constants
INVADER_SPEED_BASE = 0.5
PLAYER_SHOT_SPEED_BASE = 0.1
INVADER_SHOT_SPEED_BASE = 0.1
PLAYER_MOVE_SPEED = 5  # Base movement speed
DODGE_DISTANCE = 20    # Distance to move when dodging a shot
CORNER_MOVE_TIMEOUT = 3  # 3 seconds in the corner before forced movement
MAX_LEVEL = 100
MIN_INTELLIGENCE = 45  # Minimum intelligence value for both player and invader

# AI intelligence levels (1-100)
player_intelligence = 45
invader_intelligence = 45

# Game variables
level = 1
invader_speed = INVADER_SPEED_BASE
player_shot_speed = PLAYER_SHOT_SPEED_BASE
invader_shot_speed = INVADER_SHOT_SPEED_BASE
player_wins = 0
invader_wins = 0
total_games_played = 0
game_over = False
game_running = True
player_lives = 3  # Player starts with 5 lives

# Timing for forced movement and delays for optimization
corner_timer = None
player_in_corner = False
INVADER_MOVE_DELAY = 0.02  # Delay between invader movements
PLAYER_MOVE_DELAY = 0.1
invader_move_timer = time.monotonic()
player_move_timer = time.monotonic()

# Create player
player = Rect(display.width // 2 - 10, display.height - 20, 20, 10, fill=0x00FF00)
screen.append(player)

# Create level and wins display
level_label = label.Label(terminalio.FONT, text=f"Level: {level}", color=0xFFFFFF)
level_label.x = 5
level_label.y = 5
screen.append(level_label)

# Create player and invader wins labels
player_wins_label = label.Label(terminalio.FONT, text=f"Player Wins: {player_wins}", color=0x00FF00)
player_wins_label.x = 5
player_wins_label.y = 20
screen.append(player_wins_label)

invader_wins_label = label.Label(terminalio.FONT, text=f"Invader Wins: {invader_wins}", color=0xFF0000)
invader_wins_label.x = 5
invader_wins_label.y = 35
screen.append(invader_wins_label)

# Create total games played label
games_played_label = label.Label(terminalio.FONT, text=f"Total Games: {total_games_played}", color=0xFFFF00)
games_played_label.x = 5
games_played_label.y = 50
screen.append(games_played_label)

# Create player lives label
lives_label = label.Label(terminalio.FONT, text=f"Lives: {player_lives}", color=0x00FF00)
lives_label.x = display.width - 60
lives_label.y = 5
screen.append(lives_label)

# Create invaders and store their exact positions as floats
invaders = []
invader_positions = []

def create_invaders():
    global invaders, invader_positions, invader_direction
    invaders = []
    invader_positions = []
    invader_direction = 1

    num_rows = get_invader_rows()  # Determine the number of rows based on the level
    row_colors = [0xFF0000, 0x0000FF, 0xFFFF00]  # Colors for each row (Red, Blue, Yellow)

    for row in range(num_rows):
        for i in range(10):
            invader = Rect(10 + (i * 15), 10 + row * 15, 10, 10, fill=row_colors[row])
            invaders.append(invader)
            invader_positions.append(10 + (i * 15))  # Store the initial position as a float
            screen.append(invader)

def get_invader_rows():
    """
    Determines how many rows of invaders should be displayed based on the level.
    1 row for early levels, 2 rows at 1/3 of the way, and 3 rows at 2/3 of the way.
    """
    if level >= (MAX_LEVEL * 2) // 3:
        return 3  # 3 rows in the last third of levels
    elif level >= MAX_LEVEL // 3:
        return 2  # 2 rows in the middle third of levels
    else:
        return 1  # 1 row in the first third of levels

def move_invaders():
    global invader_direction, invader_move_timer
    if time.monotonic() - invader_move_timer > INVADER_MOVE_DELAY:  # Throttle invader movement
        for i in range(len(invaders)):
            invader_positions[i] += invader_direction * invader_speed  # Update the float position
            invaders[i].x = int(invader_positions[i])  # Set the integer value for display

        # Change direction when reaching the edge of the screen
        if any(invader.x <= 0 or invader.x >= display.width - invader.width for invader in invaders):
            invader_direction *= -1
            for invader in invaders:
                invader.y += 10  # Move invaders down
        invader_move_timer = time.monotonic()  # Reset the timer

def player_move():
    global corner_timer, player_in_corner, player_move_timer

    if time.monotonic() - player_move_timer > PLAYER_MOVE_DELAY:  # Throttle player movement
        # Check if player is staying in a corner
        if player.x <= 0 or player.x >= display.width - player.width:
            if not player_in_corner:
                player_in_corner = True
                corner_timer = time.monotonic()  # Start corner timer
            elif time.monotonic() - corner_timer >= CORNER_MOVE_TIMEOUT:
                # Force player to move out of corner after timeout
                if player.x <= 0:
                    player.x += PLAYER_MOVE_SPEED * 2  # Move right
                elif player.x >= display.width - player.width:
                    player.x -= PLAYER_MOVE_SPEED * 2  # Move left
                player_in_corner = False  # Reset corner status after moving
        else:
            player_in_corner = False  # Reset corner status when player is not in a corner

        # Perform small random human-like movements when not dodging
        if random.random() < 0.3:  # Increased chance of random movement
            if player.x > display.width // 2 and player.x - PLAYER_MOVE_SPEED >= 0:
                player.x -= PLAYER_MOVE_SPEED  # Small left nudge
            elif player.x < display.width // 2 and player.x + player.width + PLAYER_MOVE_SPEED <= display.width:
                player.x += PLAYER_MOVE_SPEED  # Small right nudge

        # Player will dodge based on shot proximity
        player_avoid_shots()
        player_move_timer = time.monotonic()  # Reset the timer

def player_avoid_shots():
    closest_shot = None
    min_distance = float('inf')

    # Find the closest shot to the player
    for shot in invader_shots:
        distance = abs(shot.x - player.x)
        if distance < min_distance and shot.y > player.y - 60:  # Check shots within 60 pixels vertically
            min_distance = distance
            closest_shot = shot

    # Dodge the closest shot if within a certain range
    if closest_shot and min_distance < player.width * 1.5:
        if closest_shot.x < player.x and player.x + player.width + DODGE_DISTANCE <= display.width:
            player.x += DODGE_DISTANCE  # Dodge right
        elif closest_shot.x > player.x and player.x - DODGE_DISTANCE >= 0:
            player.x -= DODGE_DISTANCE  # Dodge left

    # Ensure player stays within bounds after dodging
    player.x = max(0, min(player.x, display.width - player.width))

def shoot():
    if invaders and player_intelligence > random.randint(0, 100):
        # Find invader closest to player.x to shoot
        closest_invader = min(invaders, key=lambda invader: abs(invader.x - player.x))
        if closest_invader and abs(closest_invader.x - player.x) < 50:  # Shoot only when aligned and close
            shot_x = player.x + player.width // 2 - 2
            shot = Rect(shot_x, player.y - 10, 4, 10, fill=0xFFFFFF)
            shots.append(shot)
            screen.append(shot)

def invader_shoot():
    if invaders and invader_intelligence > random.randint(0, 100):
        # Target the player's position more accurately
        shooting_invader = min(invaders, key=lambda invader: abs(invader.x - player.x))
        shot_x = shooting_invader.x + shooting_invader.width // 2 - 2
        shot = Rect(shot_x, shooting_invader.y + 10, 4, 10, fill=0xFFFF00)
        invader_shots.append(shot)
        screen.append(shot)

def move_shots():
    for shot in shots[:]:
        shot.y -= int(player_shot_speed * 20)
        if shot.y < 0:
            screen.remove(shot)
            shots.remove(shot)

    for shot in invader_shots[:]:
        shot.y += int(invader_shot_speed * 20)
        if shot.y > display.height:
            screen.remove(shot)
            invader_shots.remove(shot)

def check_collisions():
    global game_over, player_lives
    for shot in shots[:]:
        for invader in invaders[:]:
            if (shot.x < invader.x + invader.width and
                shot.x + shot.width > invader.x and
                shot.y < invader.y + invader.height and
                shot.height + shot.y > invader.y):
                screen.remove(invader)
                invaders.remove(invader)
                screen.remove(shot)
                shots.remove(shot)
                break
    
    for shot in invader_shots[:]:
        if (shot.x < player.x + player.width and
            shot.x + shot.width > player.x and
            shot.y < player.y + player.height and
            shot.height + shot.y > player.y):
            player_lives -= 1
            lives_label.text = f"Lives: {player_lives}"
            screen.remove(shot)
            invader_shots.remove(shot)
            if player_lives <= 0:
                game_over = True
                show_game_over("Invaders Win!")
            break

def show_game_over(winner_text):
    global player_wins, invader_wins, total_games_played
    # Center the winner text
    text_area = label.Label(terminalio.FONT, text=winner_text, color=0xFFFFFF)
    text_area.x = (display.width - len(winner_text) * 6) // 2  # Approximate character width to center text
    text_area.y = display.height // 2 - 10  # Center vertically
    screen.append(text_area)
    
    time.sleep(5)  # Wait for 5 seconds before restarting the game
    screen.remove(text_area)

    # Update wins and total games
    total_games_played += 1
    games_played_label.text = f"Total Games: {total_games_played}"

    if "Player Wins!" in winner_text:
        player_wins += 1
        player_wins_label.text = f"Player Wins: {player_wins}"
        update_backlight()  # Update backlight based on wins
        level_up()
    else:
        invader_wins += 1
        invader_wins_label.text = f"Invader Wins: {invader_wins}"
        update_backlight()  # Update backlight based on wins
        reset_game()

def level_up():
    global level, player_intelligence, invader_intelligence, invader_speed, player_shot_speed, invader_shot_speed
    level += 1
    if level > MAX_LEVEL:
        level = 1
        # Reset intelligence when the level resets to 1
        player_intelligence = MIN_INTELLIGENCE
        invader_intelligence = MIN_INTELLIGENCE

    level_label.text = f"Level: {level}"
    
    # Increase intelligence and other parameters if not resetting to level 1
    if level != 1:
        player_intelligence = min(player_intelligence + 3, 100)
        invader_intelligence = min(invader_intelligence + 3, 100)
    
    invader_speed = INVADER_SPEED_BASE + level * 0.02  # Slightly slower speed increase
    player_shot_speed += 0.008  # Slower shot speed increase
    invader_shot_speed += 0.008
    reset_game()

def reset_game():
    global shots, invader_shots, game_over, player_lives
    player_lives = 3  # Reset lives at the start of a new game
    lives_label.text = f"Lives: {player_lives}"
    # Remove all invaders and shots, but leave player and level label intact
    for obj in invaders + shots + invader_shots:
        screen.remove(obj)
    create_invaders()  # Recreate invaders with updated rows based on level
    shots = []
    invader_shots = []
    game_over = False

# Start initial game
shots = []
invader_shots = []
create_invaders()
display.show(screen)
update_backlight()  # Set the initial state of the backlight

# Main game loop with cooperative multitasking
shoot_timer = 0
invader_shoot_timer = 0

while game_running:
    current_time = time.monotonic()

    if not game_over:
        # Move invaders more frequently for faster movement
        move_invaders()

        # Move player at regular intervals
        player_move()

        # Move shots at regular intervals
        move_shots()

        # Check for collisions
        check_collisions()

        # Auto shoot every 1.5 seconds for both the player and invaders
        shoot_timer += 1
        if shoot_timer >= 30:  # Shoot more frequently
            shoot()
            shoot_timer = 0

        invader_shoot_timer += 1
        if invader_shoot_timer >= 40:
            invader_shoot()
            invader_shoot_timer = 0

        # Check if invaders reach the player
        for invader in invaders:
            if invader.y + invader.height >= player.y:
                game_over = True
                show_game_over("Invaders Win!")
                break

        # Check if all invaders are destroyed
        if len(invaders) == 0:
            game_over = True
            show_game_over("Player Wins!")

    else:
        time.sleep(2)
        reset_game()

    time.sleep(0.01)  # Small delay to prevent maxing out CPU

while True:
    pass  # Keeps the program running after the game ends

