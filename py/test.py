# Imports go at the top
from microbit import *

# Code in a 'while True:' loop repeats forever
while True:
    display.show(Image.HAPPY)
    sleep(1000)
    display.scroll('HELLO WORLD!')

