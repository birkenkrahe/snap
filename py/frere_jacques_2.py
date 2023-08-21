from microbit import *
import music

# Define the song
frere_jacques = [
    'C4:4', 'D4:4', 'E4:4', 'C4:4',  # Frère Jacques,
    'C4:4', 'D4:4', 'E4:4', 'C4:4',  # Frère Jacques,
    'E4:4', 'F4:4', 'G4:8',           # Dormez-vous?
    'E4:4', 'F4:4', 'G4:8',           # Dormez-vous?
    'G4:4', 'A4:4', 'G4:4', 'F4:4', 'E4:4', 'C4:4',  # Sonnez les matines,
    'G4:4', 'A4:4', 'G4:4', 'F4:4', 'E4:4', 'C4:4',  # Sonnez les matines,
    'C4:4', 'G3:4', 'C4:8'            # Ding, dang, dong.
    'C4:4', 'G3:4', 'C4:8'            # Ding, dang, dong.
]

# Play the song
music.play(frere_jacques)