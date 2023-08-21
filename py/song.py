from microbit import *
import music

def cover():
    display.clear()
    display.show(Image.MUSIC_QUAVERS)
    sleep(1000)
    display.scroll('Frere Jacques')
    display.show(Image.MUSIC_QUAVERS)

def song():
    for x in range(2):
        music.play(['F4','G4','A4','C4'])
    for x in range(2):
        music.play(['A4:4','Bb4:4','C5:8'])
    for x in range(2):
        music.play(['C5:2', 'D5:2', 'C5:2', 'Bb4:2',
                   'A4:4','F4:4'])
    for x in range(2):
        music.play(['F4:4','C4:4','F4:8'])
    
while True:
    # show music symbols and song title
    cover()
    # Frere Jacques - French nursery rhyme
    song()
    sleep(1000)
    break
display.clear()