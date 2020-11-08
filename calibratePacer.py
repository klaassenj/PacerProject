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
speedOptions = [(x * 15 + 320) for x in range(0, 10)]
resp = 2
sensorA = 23
sensorB = 12
sensorC = 16
sensorD = 18
servoMin = 220
servoMax = 400
pulseFrequency = 50 # ESC takes 50 Hz

stopRC = False

pwm.set_pwm_freq(pulseFrequency)
pi = pigpio.pi()
 
def getStop():
    return motorMin

def followLines(pwm, pi, servoMin, servoMax, steerPercent, sampleRate, sensorA, sensorB, sensorC, sensorD):
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
                leftSignal = pi.read(sensorA)
                rightSignal = pi.read(sensorD)
                middleSignal = pi.read(sensorB) + pi.read(sensorC) 
                if(middleSignal == 0):
		    direction = servoMiddle
		elif(leftSignal == 0):
                    # Turn Left
                    direction -= steeringAmount
		elif(rightSignal == 0):
		    direction += steeringAmount	
                else:
                    # Revert to Straight
                    direction = servoMiddle
                pwm.set_pwm(0, 0, int(direction))
                time.sleep(1/sampleRate)
        except KeyboardInterrupt:
            print('Keyboard Interrupted. Stopping...')
            pi.stop()
            pwm.set_pwm(0, 0, servoMiddle)
            time.sleep(1)


try:
    thread.start_new_thread(followLines, (pwm, pi, servoMin, servoMax, steerPercent, sampleRate, sensorA, sensorB, sensorC, sensorD))
except:
    print("Steering or Kill Switch Thread Failed to Start")
    

current_movement = getStop()


# get the curses screen window
screen = curses.initscr()
 
# turn off input echoing
curses.noecho()
 
# respond to keys immediately (don't wait for enter)
curses.cbreak()
 
# map arrow keys to special values
screen.keypad(True)
 
# press s to stop 
try:
    while not stopRC:
        char = screen.getch()
        screen.clear()
        move = False
        if char == ord('q'):
            break
        elif char == curses.KEY_UP:
            if current_movement < motorMax:
                current_movement += resp 
                move = True
            screen.addstr(0, 0, 'up   ' + str(current_movement))       
        elif char == curses.KEY_DOWN:
            if current_movement > motorMin:
                current_movement -= resp 
                move = True
            screen.addstr(0, 0, 'down    ' + str(current_movement))
        elif char == ord('\n'):
            current_movement = motorMin 
            move = True
            screen.addstr(0, 0, 'Stoppp    ' + str(current_movement))     
        elif 48 <= char and char <= 57:
            index = int(char) - 48
            current_movement = speedOptions[index] 
            move = True
            screen.addstr(0, 0, 'Speed Set at    ' + str(index) + ":  "+ str(current_movement))
        elif char == ord('s'):
            # stop everything 
            current_movement = getStop() 
            current_turn_position  = getCenter()
            screen.addstr(0, 0, 'up    ' + str(current_movement) + ' and down ' + str(current_turn_position))       
            move = True
        
        if move:
            pwm.set_pwm(1, 0, current_movement)
finally:
    # shut down cleanly
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()
    pwm.set_pwm(1, 0, motorMin)
    time.sleep(1)

