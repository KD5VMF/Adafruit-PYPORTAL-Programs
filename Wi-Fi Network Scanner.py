import board
import terminalio
from adafruit_display_text import label
from adafruit_esp32spi import adafruit_esp32spi
import displayio
from digitalio import DigitalInOut
import time

# Title: Wi-Fi Network Scanner
# About: This program scans for available Wi-Fi networks and displays their SSID, signal strength (RSSI),
#        and channel on the PyPortal display using an adjustable font for better readability.
# Author: [Your Name]
# Date: [Today's Date]

# Initialize the PyPortal display
display = board.DISPLAY

# Wi-Fi coprocessor setup using SPI
spi = board.SPI()

# Initialize ESP32 pins
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

# Initialize ESP32 SPI control
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

# Create a display group (a container for display elements)
splash = displayio.Group()
display.show(splash)

# Set up the title label at the top of the display
title_label = label.Label(terminalio.FONT, text="Scanning Wi-Fi - 2.4Ghz...", color=0xFFFFFF, x=10, y=10)
splash.append(title_label)

# List to keep track of labels for dynamic updating
dynamic_labels = []

# Function to create and configure labels
def create_label(text, y_offset, color):
    lbl = label.Label(terminalio.FONT, text=text, x=10, y=y_offset)
    lbl.color = color
    return lbl

y_offset = 30  # Initial vertical offset for the first label

while True:
    try:
        # Scan for Wi-Fi networks
        scan_results = esp.scan_networks()

        # Sort results by RSSI (signal strength) in descending order
        sorted_scan_results = sorted(scan_results, key=lambda x: x['rssi'], reverse=True)

        # Clear existing dynamic labels from the display
        for old_label in dynamic_labels:
            splash.remove(old_label)
        dynamic_labels.clear()

        # Add new labels for each Wi-Fi network found
        for entry in sorted_scan_results:
            ssid = entry['ssid'].decode("utf-8")  # Decode SSID from bytes to string
            rssi = entry['rssi']
            channel = entry['channel']

            # Choose label color based on signal strength
            if rssi > -50:
                color = 0x00FF00  # Strong signal (Green)
            elif rssi > -70:
                color = 0xFFFF00  # Medium signal (Yellow)
            else:
                color = 0xFF0000  # Weak signal (Red)

            # Format the display text for each network
            display_text = f"SSID: {ssid}, RSSI: {rssi}, Ch: {channel}"
            text_label = create_label(display_text, y_offset, color)
            splash.append(text_label)
            dynamic_labels.append(text_label)  # Track the label for later removal

            y_offset += 20  # Increment y-offset for the next label

        # Reset the y-offset for the next scan
        y_offset = 30

    except Exception as e:
        # Display error message if the scan fails
        error_label = create_label(f"An error occurred: {e}", y_offset, 0xFF0000)
        splash.append(error_label)
        dynamic_labels.append(error_label)

    # Wait for 10 seconds before scanning again
    time.sleep(10)  # Corrected typo 'Sleep' to 'sleep'
