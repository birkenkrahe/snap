from microbit import *

# Define the sequence of LEDs for the clockwise pattern
led_sequence = [
    (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
    (4, 1), (4, 2), (4, 3), (4, 4),
    (3, 4), (2, 4), (1, 4), (0, 4),
    (0, 3), (0, 2), (0, 1)
]

# Keep track of the current LED
current_led = 0

# Start an infinite loop
while True:
    # Turn off all LEDs
    display.clear()

    # Light up the current LED
    x, y = led_sequence[current_led]
    display.set_pixel(x, y, 9)

    # Move to the next LED
    current_led = (current_led + 1) % len(led_sequence)

    # Pause for 1 second (1000 milliseconds)
    sleep(1000)
