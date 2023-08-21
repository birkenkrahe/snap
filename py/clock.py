from microbit import *

# clear display
display.clear()

while True:
    display.show(Image('00900:'   # hand up
                       '00900:'
                       '00900'
                       '00000'
                       '00000'))
    sleep(1000) 
    display.clear()
    display.show(Image('00000:'   # hand right   
                       '00000:'
                       '00999'
                       '00000'
                       '00000'))
    sleep(1000)
    display.clear()
    display.show(Image('00000:'   # hand down
                       '00000:'
                       '00900:'
                       '00900:'
                       '00900:'))
    sleep(1000)
    display.clear()
    display.show(Image('00000:'   # hand left
                       '00000:'
                       '99900:'
                       '00000:'
                       '00000:'))
    sleep(1000)
    display.clear()