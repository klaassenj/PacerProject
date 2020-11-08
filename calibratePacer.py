'''
Pacer Project Operational Logic

Modified from http://www.codehaven.co.uk/using-arrow-keys-with-inputs-python/
Modified from: Udayan Kumar
Author: Jason Klaassen

Hardware Setup
	Raspberry Pi 3B+
	4 Generic IR sensors on pins 12, 16, 18, 23
		These sensors must have their potentiometer tuned for
		the track in the shade as the shell should be modified
		to block all sunlight from reaching underneath the vehicle
		and fooling the sensors 
	Serial Cable for Debugging
	Anker 10,000 mAh Battery Bank
	Adafruit PCA9685 Servo Driver on the SDA and SLK pins
	Traxxas Slash 2WD RC Truck - Duct tape added to block sunlight
		from getting underneath and messing with sensors.
	Fritzing Diagram available in Pacer.fzz
Inputs: 
	arg1 - integer between 1 - 10 - Describes how fast turning
		should accelerate when encountering a white line
	arg2 - integer - Describes the sampleRate or logical updates
		per second. Multiplied by 10 to be easier to type without
		a screen. Ex. 3 >>> 30 ups, 12 >>> 120 ups
	arg3 - integer - Exact PWM signal for ESC Speed. Ex. 350 or 430
		general range between 330 (5mph)  -  450 (17+ mph)

Usage:

	Once running, number keys 1 - 9 can be used to set the car to predefined
		speed ( 1 >> 330, 2, >> 340, ..., 9 >> 410 )
	
	The '0' and 'Enter' keys will stop the motor, so the car will coast
	to a stop. Since PWM is used not PPM, there is no brake. Using PPM 
	would be a nice upgrade, but unecessary for Pacing.
	
	The 'P' key sets the car to run at the 'preferredSpeed' set by arg3.
	This is great for calibrating..
'''
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
preferredSpeed = -1
if(len(args) > 1):
    steerPercent = int(args[1]) / 100
if(len(args) > 2):
    sampleRate = int(args[2]) * 10
if(len(args) > 3):
    preferredSpeed = int(args(3))
    
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
        elif char == ord('p'):
	    if(320 < preferredSpeed < 440):
	        current_movement = preferredSpeed
	    else:
		current_movement = 340
	    move = True
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

