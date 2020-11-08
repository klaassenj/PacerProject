# Helps to figure out Max and Min values for ESC
# Using Right and Left Arrow keys, one can figure out Max and Min turn values
# Using Up and Down Arrow keys, one can settle on a speed limits suitable for the future task.
# Modified from http://www.codehaven.co.uk/using-arrow-keys-with-inputs-python/
# Author: Udayan Kumar
from __future__ import division
import curses
import time
# Import the PCA9685 module.
import Adafruit_PCA9685
# Import Pigpio for reading IR
import pigpio
import thread
import sys

pwm = Adafruit_PCA9685.PCA9685()
args = sys.argv
file = args[0]
steerPercent = 0.05
sampleRate = 60

if(len(args) > 1):
    steerPercent = int(args[1]) / 100
if(len(args) > 2):
    sampleRate = int(args[2]) * 10
    
motorMin = 300
motorMax = 400
speedOptions = [(x * 10 + 320) for x in range(0, 10)]
resp = 2
leftIR = 18
rightIR = 23
remotePin = 12
servoMin = 220
servoMax = 400
pulseFrequency = 50 # ESC takes 50 Hz

stopRC = False

pwm.set_pwm_freq(pulseFrequency)
pi = pigpio.pi()
 
def getStop():
    return motorMin

def followLines(pwm, pi, servoMin, servoMax, steerPercent, sampleRate, leftIR, rightIR):
    #Initialize Variables
    leftSignal = 1
    rightSignal = 1
    servoMiddle = (servoMax + servoMin) // 2
    direction = servoMiddle
    steeringAmount = (servoMax - servoMin) * steerPercent
    if pi.connected:
        try:
            while True:
                # Read IRs
                leftSignal = pi.read(leftIR)
                rightSignal = pi.read(rightIR)
                if(leftSignal == 0):
                    # Turn Left
                    direction -= steeringAmount
                else:
                    # Revert to Straight
                    direction = servoMiddle
                pwm.set_pwm(0, 0, int(direction))
                time.sleep(1/sampleRate)
        except KeyboardInterrupt:
            print('Keyboard Interrupted. Stopping...')
            pi.stop()
            pwm.set_pwm(0, 0, servoMax)
            time.sleep(1)

def killSwitch(pwm, pi, remotePin):
	global stopRC
	currentTotal = 0
	counter = 0
	while 1:
		killSwitchReading = pi.read(remotePin)
		currentTotal += killSwitchReading
		counter += 1
		if(counter % 100 == 0):
			print("Average:", currentTotal)
			currentTotal = 0
		time.sleep(0.001)
			
	

try:
    thread.start_new_thread(followLines, (pwm, pi, servoMin, servoMax, steerPercent, sampleRate, leftIR, rightIR))
    thread.start_new_thread(killSwitch, (pwm, pi, remotePin))
except:
    print("Steering or Kill Switch Thread Failed to Start")
    
while 1:
	pass
