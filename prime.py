import time
import board
import displayio
from adafruit_display_text import label
import terminalio

# Setup display
display = board.DISPLAY
display_group = displayio.Group()
display.show(display_group)

# Function to create and display text
def display_text(text, y=30):
    # Clear the previous display group
    while display_group:
        display_group.pop()

    text_area = label.Label(terminalio.FONT, text=text, color=0x00FF00, x=10, y=y)
    display_group.append(text_area)
    display.refresh()

# Function to check if a number is prime
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# Main loop to calculate and display prime numbers
current_number = 2
while True:
    if is_prime(current_number):
        display_text(f"Prime: {current_number}")
        #time.sleep(0.5)  # Add a small delay to see the primes
    current_number += 1
