from BirdBrain import Finch
import time

myFinch = Finch('A')

for i in range(0,10):
    myFinch.setBeak(100, 100, 100)
    time.sleep(1)
    myFinch.setBeak(0, 0, 0)
    time.sleep(1)
	
myFinch.stopAll()
