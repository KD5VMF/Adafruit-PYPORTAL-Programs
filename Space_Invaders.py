import board
import displayio
import time
import random
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio

# Setup display
display = board.DISPLAY
screen = displayio.Group()

# Constants
INVADER_SPEED_BASE = 0.5
PLAYER_SHOT_SPEED_BASE = 0.1
INVADER_SHOT_SPEED_BASE = 0.1
PLAYER_MOVE_SPEED_SMALL = 3
PLAYER_MOVE_SPEED_MEDIUM = 5
PLAYER_MOVE_SPEED_LARGE = 8
PLAYER_MOVE_SPEED_FAR = 12  # For far, human-like moves
MAX_LEVEL = 100

# AI intelligence levels (1-100)
player_intelligence = 50
invader_intelligence = 50

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
player_direction = 1  # Player movement direction

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

# Create invaders and store their exact positions as floats
invaders = []
invader_positions = []

def create_invaders():
    global invaders, invader_positions, invader_direction
    invaders = []
    invader_positions = []
    invader_direction = 1
    for i in range(10):
        invader = Rect(10 + (i * 15), 10, 10, 10, fill=0xFF0000)
        invaders.append(invader)
        invader_positions.append(10 + (i * 15))  # Store the initial position as a float
        screen.append(invader)

def move_invaders():
    global invader_direction
    for i in range(len(invaders)):
        invader_positions[i] += invader_direction * invader_speed  # Update the float position
        invaders[i].x = int(invader_positions[i])  # Set the integer value for display

    # Change direction when reaching the edge of the screen
    if any(invader.x <= 0 or invader.x >= display.width - invader.width for invader in invaders):
        invader_direction *= -1
        for invader in invaders:
            invader.y += 10  # Move invaders down

def player_move():
    global player, player_direction, player_intelligence
    # Force player to keep moving to prevent staying in one place
    move_distance = random.choice([PLAYER_MOVE_SPEED_SMALL, PLAYER_MOVE_SPEED_MEDIUM, PLAYER_MOVE_SPEED_LARGE, PLAYER_MOVE_SPEED_FAR])

    if player_intelligence > random.randint(0, 100):
        if player_direction == 1:  # Move right
            if player.x + player.width < display.width:
                player.x += move_distance
            else:
                player_direction = -1  # Change direction
        elif player_direction == -1:  # Move left
            if player.x > 0:
                player.x -= move_distance
            else:
                player_direction = 1  # Change direction

        # Randomly change direction based on intelligence
        if random.random() < player_intelligence / 200:  # Higher intelligence means more deliberate direction changes
            player_direction *= -1

def shoot():
    # Player shoots from its current position towards a random invader, more intelligent shots if AI level is high
    if invaders and player_intelligence > random.randint(0, 100):
        target_invader = random.choice(invaders)
        shot_x = player.x + player.width // 2 - 2  # Shoot from the center of the player
        shot = Rect(shot_x, player.y - 10, 4, 10, fill=0xFFFFFF)
        shots.append(shot)
        screen.append(shot)

def invader_shoot():
    # Invaders shoot from their current positions towards the player, smarter shots as intelligence increases
    if invaders and invader_intelligence > random.randint(0, 100):
        shooting_invader = random.choice(invaders)
        shot_x = shooting_invader.x + shooting_invader.width // 2 - 2  # Shoot from the center of the invader
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
    global game_over
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
        level_up()
    else:
        invader_wins += 1
        invader_wins_label.text = f"Invader Wins: {invader_wins}"
        reset_game()

def level_up():
    global level, player_intelligence, invader_intelligence, invader_speed, player_shot_speed, invader_shot_speed
    if level >= MAX_LEVEL:
        level = 1  # Restart at level 1 after reaching level 100
    else:
        level += 1

    level_label.text = f"Level: {level}"  # Update level display
    player_intelligence = min(player_intelligence + 10, 100)  # Increase player intelligence up to a max of 100
    invader_intelligence = min(invader_intelligence + 10, 100)  # Increase invader intelligence up to a max of 100
    invader_speed = INVADER_SPEED_BASE + level * 0.05  # Increase invader speed
    player_shot_speed += 0.02  # Increase player shot speed each level
    invader_shot_speed += 0.02  # Increase invader shot speed each level
    reset_game()

def reset_game():
    global shots, invader_shots, game_over
    # Remove all invaders and shots, but leave player and level label intact
    for obj in invaders + shots + invader_shots:
        screen.remove(obj)
    create_invaders()
    shots = []
    invader_shots = []
    game_over = False

# Start initial game
shots = []
invader_shots = []
create_invaders()
display.show(screen)

# Main game loop with cooperative multitasking
shoot_timer = 0
invader_shoot_timer = 0
invader_move_timer = time.monotonic()
player_move_timer = time.monotonic()

while game_running:
    current_time = time.monotonic()

    if not game_over:
        # Move invaders more frequently for faster movement
        if current_time - invader_move_timer > 0.01:  # Reduced delay for faster movement
            move_invaders()
            invader_move_timer = current_time

        # Move player at regular intervals
        if current_time - player_move_timer > 0.1:
            player_move()
            player_move_timer = current_time

        # Move shots at regular intervals
        move_shots()

        # Check for collisions
        check_collisions()

        # Auto shoot every 2 seconds for both the player and invaders
        shoot_timer += 1
        if shoot_timer >= 40:
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
