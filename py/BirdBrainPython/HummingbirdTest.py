from BirdBrain import Hummingbird, Microbit
import time

myBird    = Hummingbird('A')

for i in range(0,10):
	myBird.setLED(1,100)
	time.sleep(1)
	myBird.setLED(1,0)
	time.sleep(1)
		
myBird.stopAll()
