greenLED = 16
blueLED = 12
leftIR = 18
rightIR = 23

servoMin = 250
servoMax = 400
servoMiddle = (400 - 250) // 2


pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=0)

from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685

import pigpio
import time

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
        pwm.set_pwm(0, 0, direction)
        time.sleep(0.1)
        direction += 1
        if(direction > servoMax):
            direction = servoMin
            time.sleep(1)
except KeyboardInterrupt:
    print("Testing Complete.")
    direction = servoMiddle
    pwm.set_pwm(0, 0, direction)
    time.sleep(1)



if not pi.connected:
    exit();
else:
    while True:
        try:
            leftSignal = pi.read(leftIR)
            rightSignal = pi.read(rightIR)
            if(leftSignal == 0):
                steerLeft()
            else:
                revertToStraight()
            pwm.set_pwm(0, 0, direction)
            time.sleep(1/60)
        except KeyboardInterrupt:
            print('Keyboard Interrupted. Stopping...')
            pi.stop()
            time.sleep(1)




