from microbit import *

# Set your initial time
hours = 12
minutes = 0

# Infinite loop to update the time
while True:
    # Display hours (left 3 columns)
    for i in range(hours):
        display.set_pixel(i % 3, i // 3, 9)

    # Display separator (middle column)
    for i in range(5):
        display.set_pixel(3, i, 9 if i % 2 == 0 else 0)

    # Display minutes (right 2 columns)
    for i in range(minutes // 10):
        display.set_pixel(4, i, 9)
    for i in range(minutes % 10):
        display.set_pixel(5, i, 9)

    # Wait for one minute
    sleep(60000)

    # Increment time
    minutes += 1
    if minutes == 60:
        minutes = 0
        hours += 1
    if hours == 24:
        hours = 0
