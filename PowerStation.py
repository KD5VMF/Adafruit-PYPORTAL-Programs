import time
import board
import displayio
from adafruit_display_text import label
import terminalio
import random

# Create a display context
display = board.DISPLAY

# Fill the screen with a black background
color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  # Black

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
display_group = displayio.Group()
display_group.append(bg_sprite)

# Function to create text labels
def create_label(text, y, color=0x00FF00):
    text_area = label.Label(terminalio.FONT, text=text, color=color, x=10, y=y)
    return text_area

# Simulated data fields for a power station
data_labels = [
    "Core Temperature:",
    "Reactor Status:",
    "Energy Output:",
    "Coolant Level:",
    "Control Rods Position:",
    "Turbine Speed:",
    "Radiation Level:",
    "External Power Grid:",
    "Emergency Systems Status:",
    "Water Reserve:"
]

# Generate initial labels
y_position = 10
labels = []
for data_label in data_labels:
    text_label = create_label(f"{data_label} Initializing...", y_position)
    display_group.append(text_label)
    labels.append(text_label)
    y_position += 20

display.show(display_group)

def update_data():
    # Simulated data updates specific to a power station
    labels[0].text = f"Core Temperature: {random.randint(250, 800)} C"
    labels[1].text = "Reactor Status: " + random.choice(["Operational", "Shutdown", "Standby", "Critical"])
    labels[2].text = f"Energy Output: {random.randint(300, 1500)} MW"
    labels[3].text = f"Coolant Level: {random.randint(50, 100)}%"
    labels[4].text = f"Control Rods Position: {random.randint(0, 100)}%"
    labels[5].text = f"Turbine Speed: {random.randint(1500, 3600)} RPM"
    labels[6].text = f"Radiation Level: {random.randint(1, 50)} mSv/h"
    labels[7].text = "External Power Grid: " + random.choice(["Stable", "Fluctuating", "Overloaded"])
    labels[8].text = "Emergency Systems Status: " + random.choice(["Active", "Inactive", "Testing"])
    labels[9].text = f"Water Reserve: {random.randint(200, 500)} KL"

while True:
    update_data()
    display.refresh()
    time.sleep(1)  # Update every 2 seconds for new data simulation
