from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685

import pigpio
import time


leftIR = 18
rightIR = 23


servoMin = 260
servoMax = 490
servoMiddle = (servoMax + servoMin) // 2

steeringPercentage = 0.05
steeringAmount = (servoMax - servoMin) * steeringPercentage

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



leftSignal = 1
rightSignal = 1
direction = servoMiddle


def steerLeft(direction):
    return direction + steeringAmount

def revertToStraight():
    return servoMiddle


if not pi.connected:
    exit();
else:
    while True:
        try:
            leftSignal = pi.read(leftIR)
            rightSignal = pi.read(rightIR)
            if(leftSignal == 0):
                direction = steerLeft(direction)
            else:
                direction = revertToStraight()
            pwm.set_pwm(0, 0, int(direction))
            time.sleep(1/60)
        except KeyboardInterrupt:
            print('Keyboard Interrupted. Stopping...')
            pi.stop()
            pwm.set_pwm(0, 0, servoMax)
            time.sleep(1)




