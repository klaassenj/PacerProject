from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685

import pigpio
import time


leftIR = 18
rightIR = 23

servoMin = 200
servoMax = 500
servoMiddle = (servoMax + servoMin) // 2


pwm = Adafruit_PCA9685.PCA9685()



pi = pigpio.pi()

def lightLED(pi, pin):
    pi.write(pin, 1)
    
def clearAll(pi):
    pi.write(greenLED, 0)
    pi.write(blueLED, 0)

def flashLEDs(pi):
    pi.write(12, 1)
    pi.write(16, 0)
    time.sleep(1)
    pi.write(12, 0)
    pi.write(16, 1)
    time.sleep(1)


def steerLeft():
    direction -= amount

def revertToStraight():
    direction = servoMiddle


leftSignal = 1
rightSignal = 1
direction = servoMin

try:
    while True:
        print(direction)
        pwm.set_pwm(0, 0, direction)
        time.sleep(0.1)
        direction += 2
        if(direction > servoMax):
            direction = servoMin
            time.sleep(1)
except KeyboardInterrupt:
    print("Testing Complete.")
    direction = servoMiddle
    pwm.set_pwm(0, 0, servoMax)
    time.sleep(1)
