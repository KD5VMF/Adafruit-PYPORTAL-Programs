"""
Space Invaders-Style Game for Adafruit PyPortal
===============================================

This is an enhanced "Space Invaders"-style game developed for the Adafruit PyPortal.
The player controls a green rectangle at the bottom of the screen that moves
automatically and shoots at the invaders. The invaders come in different types,
each with unique behaviors and hit points. The game includes a scoring system,
high score tracking, and visual feedback for hits.

Gameplay:
---------
- Destroy all invaders to win each level.
- The player moves left and right automatically and dodges incoming shots.
- As levels increase, invaders become more aggressive and intelligent.

Features:
---------
- Multiple invader types with distinct behaviors.
- Scoring system to track player performance.
- High score tracking saved after completing all levels (up to level 250).
- Visual feedback (e.g., color changes) when invaders are hit.
- Enhanced difficulty scaling for a progressively challenging experience.
- NeoPixel backlight feedback based on game progress.

Controls and Behavior:
----------------------
- The game runs automatically without player input.
- The player moves and shoots based on alignment with invaders.
- The game resets after completing all 250 levels, with score reset.

Optimized for PyPortal:
-----------------------
- Efficient use of resources to ensure smooth gameplay.
- Timed delays control movement and shooting updates.

Developed by: ChatGPT with Direction from Adam Figueroa
"""

import board
import displayio
import time
import random
import storage
import json
from digitalio import DigitalInOut, Direction
import busio
import adafruit_sdcard
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio
import neopixel
import microcontroller

# ---------------------------
# Setup Display and Backlight
# ---------------------------
display = board.DISPLAY
screen = displayio.Group()
display.show(screen)

# Setup the backlight (using the onboard NeoPixel)
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixels.brightness = 1.0  # Full brightness

def update_backlight():
    if player_wins > invader_wins:
        pixels.fill((0, 255, 0))  # Green for player leading
    elif invader_wins > player_wins:
        pixels.fill((255, 0, 0))  # Red for invader leading
    else:
        pixels.fill((0, 0, 0))    # Backlight off if tied

# ---------------------------
# Constants and Initial Setup
# ---------------------------
INVADER_SPEED_BASE = 0.7          # Base speed for invaders
PLAYER_SHOT_SPEED_BASE = 0.15     # Player shot speed
INVADER_SHOT_SPEED_BASE = 0.12    # Invader shot speed
PLAYER_MOVE_SPEED = 6             # Player movement speed
DODGE_DISTANCE = 25               # Distance to dodge shots
CORNER_MOVE_TIMEOUT = 2           # Seconds before forced movement from corner
MAX_LEVEL = 250                    # Updated to 250 levels
MIN_INTELLIGENCE = 50             # Minimum intelligence for AI

# AI intelligence levels (1-100)
player_intelligence = 50          # Player intelligence
invader_intelligence = 50         # Invader intelligence

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
player_lives = 10  # Player starts with 10 lives
score = 0
high_score = 0

# Timing for forced movement and updates
corner_timer = None
player_in_corner = False
INVADER_MOVE_DELAY = 0.015  # Invader movement delay in seconds
PLAYER_MOVE_DELAY = 0.08     # Player movement delay in seconds
invader_move_timer = time.monotonic()
player_move_timer = time.monotonic()

# Lists to hold game objects
invaders = []
invader_positions = []
shots = []
invader_shots = []

# ---------------------------
# Mounting the SD Card
# ---------------------------
try:
    # Initialize SPI bus
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    
    # Initialize chip select (CS) for the SD card
    # Ensure that board.SD_CS corresponds to your PyPortal's SD CS pin
    cs = DigitalInOut(board.SD_CS)
    cs.direction = Direction.OUTPUT
    cs.value = True  # Start with SD card not selected

    # Create SD card object
    sdcard = adafruit_sdcard.SDCard(spi, cs)

    # Create a filesystem object
    vfs = storage.VfsFat(sdcard)

    # Mount the filesystem to '/sd'
    storage.mount(vfs, "/sd")
    sd_present = True
    print("SD Card mounted successfully.")
except Exception as e:
    print(f"SD Card not mounted: {e}")
    sd_present = False

# ---------------------------
# High Score Management
# ---------------------------
def load_high_score():
    global high_score
    if sd_present:
        try:
            with open("/sd/highscore.json", "r") as f:
                data = json.load(f)
                high_score = data.get("high_score", 0)
                print(f"High Score loaded: {high_score}")
        except (OSError, ValueError):
            high_score = 0  # Default high score if file not found or invalid
            print(f"High score file not found or invalid. Starting at 0.")
    else:
        high_score = 0  # Cannot load high score without SD card
        print("SD card not present. High score not loaded.")

def save_high_score():
    if sd_present:
        data = {"high_score": high_score}
        try:
            with open("/sd/highscore.json", "w") as f:
                json.dump(data, f)
                print(f"High Score saved: {high_score}")
        except OSError as e:
            print(f"Failed to save high score: {e}")
            # Optionally, provide in-game feedback if possible
    else:
        pass  # Skip saving if SD card is not present

# Load the high score at the start
load_high_score()

# ---------------------------
# Create Player
# ---------------------------
player = Rect(display.width // 2 - 10, display.height - 20, 20, 10, fill=0x00FF00)
screen.append(player)

# ---------------------------
# Create Labels
# ---------------------------
level_label = label.Label(terminalio.FONT, text=f"Level: {level}", color=0xFFFFFF)
level_label.x = 5
level_label.y = 5
screen.append(level_label)

player_wins_label = label.Label(terminalio.FONT, text=f"Player Wins: {player_wins}", color=0x00FF00)
player_wins_label.x = 5
player_wins_label.y = 20
screen.append(player_wins_label)

invader_wins_label = label.Label(terminalio.FONT, text=f"Invader Wins: {invader_wins}", color=0xFF0000)
invader_wins_label.x = 5
invader_wins_label.y = 35
screen.append(invader_wins_label)

games_played_label = label.Label(terminalio.FONT, text=f"Total Games: {total_games_played}", color=0xFFFF00)
games_played_label.x = 5
games_played_label.y = 50
screen.append(games_played_label)

lives_label = label.Label(terminalio.FONT, text=f"Lives: {player_lives}", color=0x00FF00)
lives_label.x = display.width - 60
lives_label.y = 5
screen.append(lives_label)

score_label = label.Label(terminalio.FONT, text=f"Score: {score}", color=0xFFFFFF)
score_label.x = display.width // 2 - 30
score_label.y = 5
screen.append(score_label)

high_score_label = label.Label(terminalio.FONT, text=f"High Score: {high_score}", color=0xFFFF00)
high_score_label.x = display.width // 2 - 30
high_score_label.y = 20
screen.append(high_score_label)

# ---------------------------
# Invader Class
# ---------------------------
class Invader:
    def __init__(self, x, y, invader_type):
        self.type = invader_type  # 'red', 'blue', 'yellow'
        self.hit_points = 1
        self.color = 0xFF0000  # Default red
        if self.type == 'blue':
            self.hit_points = 2
            self.color = 0x0000FF
        elif self.type == 'yellow':
            self.hit_points = 3
            self.color = 0xFFFF00
        self.rect = Rect(x, y, 10, 10, fill=self.color)
        screen.append(self.rect)
        self.x_pos = float(x)
    
    def hit(self):
        self.hit_points -= 1
        if self.hit_points <= 0:
            screen.remove(self.rect)
            try:
                invaders.remove(self)
            except ValueError:
                print("Attempted to remove an invader that's not in the list.")
            return True  # Invader destroyed
        else:
            # Visual feedback: change color briefly
            original_color = self.color
            self.rect.fill = 0xFFFFFF  # White to indicate hit
            time.sleep(0.05)
            self.rect.fill = original_color
            return False  # Invader still alive

# ---------------------------
# Create Invaders
# ---------------------------
def create_invaders():
    global invaders, invader_positions, invader_direction
    invaders = []
    invader_positions = []
    invader_direction = 1

    num_rows = get_invader_rows()
    row_colors = ['red', 'blue', 'yellow']  # Types of invaders

    for row in range(num_rows):
        invader_type = row_colors[row % len(row_colors)]
        for i in range(10):
            x = 10 + (i * 15)
            y = 10 + row * 15
            invader = Invader(x, y, invader_type)
            invaders.append(invader)
            invader_positions.append(x)  # Store initial float position

# ---------------------------
# Determine Number of Invader Rows
# ---------------------------
def get_invader_rows():
    """
    Determines how many rows of invaders should be displayed based on the level.
    1 row for early levels, 2 rows at 1/3 of the way, and 3 rows at 2/3 of the way.
    """
    if level >= (MAX_LEVEL * 2) // 3:
        return 3
    elif level >= MAX_LEVEL // 3:
        return 2
    else:
        return 1

# ---------------------------
# Move Invaders
# ---------------------------
def move_invaders():
    global invader_direction, invader_move_timer
    if time.monotonic() - invader_move_timer > INVADER_MOVE_DELAY:
        for i in range(len(invaders)):
            invader_positions[i] += invader_direction * invader_speed
            invaders[i].x_pos = invader_positions[i]
            invaders[i].rect.x = int(invaders[i].x_pos)
        
        # Check for edge collision
        edge_collision = False
        for invader in invaders:
            if invader.rect.x <= 0 or invader.rect.x >= display.width - invader.rect.width:
                edge_collision = True
                break
        
        if edge_collision:
            invader_direction *= -1
            for invader in invaders:
                invader.rect.y += 10  # Move invaders down
        
        invader_move_timer = time.monotonic()

# ---------------------------
# Player Movement
# ---------------------------
def player_move():
    global corner_timer, player_in_corner, player_move_timer

    if time.monotonic() - player_move_timer > PLAYER_MOVE_DELAY:
        # Check if player is in a corner
        if player.x <= 0 or player.x >= display.width - player.width:
            if not player_in_corner:
                player_in_corner = True
                corner_timer = time.monotonic()
            elif time.monotonic() - corner_timer >= CORNER_MOVE_TIMEOUT:
                if player.x <= 0:
                    player.x = int(player.x + PLAYER_MOVE_SPEED * 2)
                elif player.x >= display.width - player.width:
                    player.x = int(player.x - PLAYER_MOVE_SPEED * 2)
                player_in_corner = False
        else:
            player_in_corner = False

        # Random human-like movements
        if random.random() < 0.4:
            if player.x > display.width // 2 and player.x - PLAYER_MOVE_SPEED >= 0:
                player.x = int(player.x - PLAYER_MOVE_SPEED)
            elif player.x < display.width // 2 and player.x + player.width + PLAYER_MOVE_SPEED <= display.width:
                player.x = int(player.x + PLAYER_MOVE_SPEED)

        # Dodge incoming shots
        player_avoid_shots()

        # Ensure player stays within bounds
        player.x = max(0, min(player.x, display.width - player.width))

        player_move_timer = time.monotonic()

# ---------------------------
# Player Dodge Mechanism
# ---------------------------
def player_avoid_shots():
    closest_shot = None
    min_distance = float('inf')

    # Find the closest invader shot approaching the player
    for shot in invader_shots:
        distance = abs(shot.x - player.x)
        if distance < min_distance and shot.y > player.y - 80:
            min_distance = distance
            closest_shot = shot

    # Dodge if a shot is within a certain range
    if closest_shot and min_distance < player.width * 2:
        if closest_shot.x < player.x and player.x + player.width + DODGE_DISTANCE <= display.width:
            player.x = int(player.x + DODGE_DISTANCE)
        elif closest_shot.x > player.x and player.x - DODGE_DISTANCE >= 0:
            player.x = int(player.x - DODGE_DISTANCE)

    # Ensure player stays within bounds after dodging
    player.x = max(0, min(player.x, display.width - player.width))

# ---------------------------
# Player Shooting
# ---------------------------
def shoot():
    global last_player_shot_time
    if invaders and player_intelligence > random.randint(0, 100):
        # Find invader closest to player's x position
        closest_invader = min(invaders, key=lambda invader: abs(invader.rect.x - player.x))
        if closest_invader and abs(closest_invader.rect.x - player.x) < 60:
            shot_x = player.x + player.width // 2 - 2
            shot = Rect(shot_x, player.y - 10, 4, 10, fill=0xFFFFFF)
            shots.append(shot)
            screen.append(shot)

# Initialize last shot time for player
last_player_shot_time = time.monotonic()

# ---------------------------
# Invader Shooting
# ---------------------------
def invader_shoot():
    global last_invader_shot_time
    if invaders and invader_intelligence > random.randint(0, 100):
        # Select invader closest to player's x position
        shooting_invader = min(invaders, key=lambda invader: abs(invader.rect.x - player.x))
        shot_x = shooting_invader.rect.x + shooting_invader.rect.width // 2 - 2
        shot = Rect(shot_x, shooting_invader.rect.y + 10, 4, 10, fill=0xFFFF00)
        invader_shots.append(shot)
        screen.append(shot)

# Initialize last shot time for invaders
last_invader_shot_time = time.monotonic()

# ---------------------------
# Move Shots
# ---------------------------
def move_shots():
    # Move player shots upwards
    for shot in shots[:]:
        shot.y -= int(player_shot_speed * 25)
        if shot.y < 0:
            try:
                screen.remove(shot)
            except ValueError:
                print("Attempted to remove a shot that's not in the screen.")
            shots.remove(shot)

    # Move invader shots downwards
    for shot in invader_shots[:]:
        shot.y += int(invader_shot_speed * 25)
        if shot.y > display.height:
            try:
                screen.remove(shot)
            except ValueError:
                print("Attempted to remove a shot that's not in the screen.")
            invader_shots.remove(shot)

# ---------------------------
# Check Collisions
# ---------------------------
def check_collisions():
    global game_over, player_lives, score, high_score

    # Check collisions between player shots and invaders
    for shot in shots[:]:
        for invader in invaders[:]:
            if (shot.x < invader.rect.x + invader.rect.width and
                shot.x + shot.width > invader.rect.x and
                shot.y < invader.rect.y + invader.rect.height and
                shot.height + shot.y > invader.rect.y):
                destroyed = invader.hit()
                try:
                    screen.remove(shot)
                except ValueError:
                    print("Attempted to remove a shot that's not in the screen.")
                shots.remove(shot)
                if destroyed:
                    score += 10  # Increase score
                    score_label.text = f"Score: {score}"
                    if score > high_score:
                        high_score = score
                        high_score_label.text = f"High Score: {high_score}"
                        save_high_score()
                break  # Move to next shot

    # Check collisions between invader shots and player
    for shot in invader_shots[:]:
        if (shot.x < player.x + player.width and
            shot.x + shot.width > player.x and
            shot.y < player.y + player.height and
            shot.height + shot.y > player.y):
            player_lives -= 1
            lives_label.text = f"Lives: {player_lives}"
            try:
                screen.remove(shot)
            except ValueError:
                print("Attempted to remove a shot that's not in the screen.")
            invader_shots.remove(shot)
            if player_lives <= 0:
                game_over = True
                show_game_over("Invaders Win!")
            break

# ---------------------------
# Show Game Over Screen
# ---------------------------
def show_game_over(winner_text):
    global player_wins, invader_wins, total_games_played, level, score
    # Display the winner text
    text_area = label.Label(terminalio.FONT, text=winner_text, color=0xFFFFFF)
    text_area.x = (display.width - len(winner_text) * 6) // 2  # Approximate centering
    text_area.y = display.height // 2 - 10
    screen.append(text_area)

    # Wait before resetting
    time.sleep(3)
    try:
        screen.remove(text_area)
    except ValueError:
        print("Attempted to remove text that's not in the screen.")

    # Update game statistics
    total_games_played += 1
    games_played_label.text = f"Total Games: {total_games_played}"

    if "Player Wins!" in winner_text:
        player_wins += 1
        player_wins_label.text = f"Player Wins: {player_wins}"
        update_backlight()

        # Check if the final level is reached
        if level >= MAX_LEVEL:
            # Compare and save high score
            if score > high_score:
                high_score = score
                high_score_label.text = f"High Score: {high_score}"
                save_high_score()
            
            # Display Game Completed message
            game_completed_text = "Game Completed!"
            text_completed = label.Label(terminalio.FONT, text=game_completed_text, color=0xFFFFFF)
            text_completed.x = (display.width - len(game_completed_text) * 6) // 2
            text_completed.y = display.height // 2 - 20
            screen.append(text_completed)
            time.sleep(3)
            try:
                screen.remove(text_completed)
            except ValueError:
                print("Attempted to remove text that's not in the screen.")

            # Reset game variables
            score = 0
            score_label.text = f"Score: {score}"
            level = 1
            level_label.text = f"Level: {level}"
            player_intelligence = MIN_INTELLIGENCE
            invader_intelligence = MIN_INTELLIGENCE
            invader_speed = INVADER_SPEED_BASE
            player_shot_speed = PLAYER_SHOT_SPEED_BASE
            invader_shot_speed = INVADER_SHOT_SPEED_BASE
        else:
            level_up()
    else:
        invader_wins += 1
        invader_wins_label.text = f"Invader Wins: {invader_wins}"
        update_backlight()
        reset_game()

# ---------------------------
# Level Up Function
# ---------------------------
def level_up():
    global level, player_intelligence, invader_intelligence, invader_speed, player_shot_speed, invader_shot_speed, PLAYER_MOVE_SPEED, DODGE_DISTANCE
    level += 1
    level_label.text = f"Level: {level}"

    # Increase intelligence more aggressively
    if level != 1:
        player_intelligence = min(player_intelligence + 6, 100)
        invader_intelligence = min(invader_intelligence + 6, 100)

    # Increase player speed and dodge distance
    PLAYER_MOVE_SPEED += 0.6
    DODGE_DISTANCE += 1.5

    # Increase invader parameters
    invader_speed = INVADER_SPEED_BASE + level * 0.025
    player_shot_speed += 0.015
    invader_shot_speed += 0.015

    reset_game()

# ---------------------------
# Reset Game Function
# ---------------------------
def reset_game():
    global shots, invader_shots, game_over, player_lives
    player_lives = 10
    lives_label.text = f"Lives: {player_lives}"
    # Note: Score is NOT reset here to accumulate across levels
    # Reset game objects safely
    for obj in invaders[:]:
        try:
            screen.remove(obj.rect)
        except ValueError:
            print("Attempted to remove an invader that's not in the screen.")
        invaders.remove(obj)
    for shot in shots[:]:
        try:
            screen.remove(shot)
        except ValueError:
            print("Attempted to remove a shot that's not in the screen.")
        shots.remove(shot)
    for shot in invader_shots[:]:
        try:
            screen.remove(shot)
        except ValueError:
            print("Attempted to remove a shot that's not in the screen.")
        invader_shots.remove(shot)

    # Recreate invaders for the new level
    create_invaders()
    game_over = False

# ---------------------------
# Initialize Game
# ---------------------------
def initialize_game():
    create_invaders()
    update_backlight()

initialize_game()

# ---------------------------
# Main Game Loop
# ---------------------------
while game_running:
    current_time = time.monotonic()

    if not game_over:
        # Move invaders
        move_invaders()

        # Move player
        player_move()

        # Move shots
        move_shots()

        # Check for collisions
        check_collisions()

        # Handle player shooting based on time intervals
        if time.monotonic() - last_player_shot_time > 1.0:  # Player shoots every 1 second
            shoot()
            last_player_shot_time = time.monotonic()

        # Handle invader shooting based on time intervals
        invader_shoot_delay = max(0.15, 3.0 - (level * 0.012))  # Decrease delay as level increases, min 0.15s
        if time.monotonic() - last_invader_shot_time > invader_shoot_delay:
            invader_shoot()
            last_invader_shot_time = time.monotonic()

        # Check if invaders have reached the player
        for invader in invaders:
            if invader.rect.y + invader.rect.height >= player.y:
                game_over = True
                show_game_over("Invaders Win!")
                break

        # Check if all invaders are destroyed
        if not invaders:
            game_over = True
            show_game_over("Player Wins!")
    else:
        time.sleep(1)
        reset_game()

    time.sleep(0.005)  # Small delay for smoother gameplay

while True:
    pass  # Keeps the program running after the game ends

