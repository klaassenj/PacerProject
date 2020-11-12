'''
Pacer Project Operational Logic

Modified from http://www.codehaven.co.uk/using-arrow-keys-with-inputs-python/
Modified from: Udayan Kumar
PID Algorithm adapted from Marcelo Rovai's C++ Algorithm - https://www.instructables.com/Line-Follower-Robot-PID-Control-Android-Setup/
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
lineTolerance = 10
preferredSpeed = -1
if(len(args) > 1):
    steerPercent = int(args[1]) / 100
if(len(args) > 2):
    sampleRate = int(args[2]) * 10
if(len(args > 3):
    lineTolerance = int(args[3])
if(len(args) > 4):
    preferredSpeed = int(args[4])
    
motorMin = 300
motorMax = 400
speedOptions = [(x * 15 + 320) for x in range(0, 10)]
resp = 2
sensorA = 23
sensorB = 12
sensorC = 16
sensorD = 18
sensorJ = 5
sensorK = 10
servoMin = 220
servoMax = 400
pulseFrequency = 50 # ESC takes 50 Hz

stopRC = False
currentThrottle = 0

pwm.set_pwm_freq(pulseFrequency)
pi = pigpio.pi()
 
def getStop():
    return motorMin

# void calculatePID()
# {
#   P = error;
#   I = I + error;
#   D = error-previousError;
#   PIDvalue = (Kp*P) + (Ki*I) + (Kd*D);
#   previousError = error;
# }


# void motorPIDcontrol()
# {
#   int leftMotorSpeed = 1500 - iniMotorPower - PIDvalue;
#   int rightMotorSpeed = 1500 + iniMotorPower - PIDvalue;
  
#   leftServo.writeMicroseconds(leftMotorSpeed);
#   rightServo.writeMicroseconds(rightMotorSpeed);
# }

def followLinesPID(pwm, pi, servoMin, servoMax, steerPercent, sampleRate, sensorA, sensorB, sensorC, sensorD, sensorX, sensorY):
    # Variables
    error = 0
    previousError = 0
    positionConstant = 25
    integralConstant = 1
    derivativeConstant = 0
    direction = servoMiddle
    try:
        while True:
            # Read IR Sensor Array
            # The 1 - swaps the 0 reading of white lines to 1 for easier logic
            left1 = 1 - pi.read(sensorA)
            left2 = 1 - pi.read(sensorB)
            left3 = 1 - pi.read(sensorC)
            centerLeft = 1- pi.read(sensorX)
            centerRight = 1 - pi.read(sensorY)
            right3 = 1 - pi.read(sensorD)
            right2 = 1 - pi.read(sensorE)
            right1 = 1 - pi.read(sensorF)
            # Calculate Error
            error = 0
            if(not centerLeft):
                error = -1
            if(not centerRight):
                error = 1
            if(left3):
                error = -2
            if(left2):
                error = -3
            if(left1):
                error = -4
            if(right3):
                error = 2
            if(right2):
                error = 3
            if(right1):
                error = 4
            # Calculate Corrective Action
            position = error
            integral += error
            derivative = error - previousError
            result = (turnConstant * position) + (integralConstant * integral) + (derivativeConstant * derivative);
            previousError = error
            # Execute CorrectiveAction
            direction = servoMiddle + result
            pwm.set_pwm(0, 0, int(direction))
            time.sleep(1/sampleRate)
    except KeyboardInterrupt:
        print('Keyboard Interrupted. Stopping...')
        pi.stop()
        pwm.set_pwm(0, 0, servoMiddle)
        time.sleep(1)

        
def followLines(pwm, pi, servoMin, servoMax, steerPercent, sampleRate, sensorA, sensorB, sensorC, sensorD, sensorJ, sensorK):
    #Initialize Variables
    leftSignal = 1
    rightSignal = 1
    middleSignal = 1
    lineLeftSignal = 1
    lineRightSIgnal = 1
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
		lineLeftSignal = pi.read(sensorJ)
		lineRightSignal = pi.read(sensorK) 
                
		if(middleSignal == 0):
		    direction = servoMiddle
		elif(leftSignal == 0):
                    # Turn Left
                    direction -= steeringAmount
		elif(rightSignal == 0):
		    direction += steeringAmount	
		elif(lineLeftSignal == 0):
		    direction -= steeringAmount / lineTolerance
		elif(lineRightSignal == 0):
		    direction += steeringAmount / lineTolerance
                else:
                    # Revert to Straight
                    direction = servoMiddle
		if(direction < 270):
			direction = 270
		elif(direction > 350):
			direction = 350
                pwm.set_pwm(0, 0, int(direction))
                time.sleep(1/sampleRate)
        except KeyboardInterrupt:
            print('Keyboard Interrupted. Stopping...')
            pi.stop()
            pwm.set_pwm(0, 0, servoMiddle)
            time.sleep(1)


try:
    thread.start_new_thread(followLines, (pwm, pi, servoMin, servoMax, steerPercent, sampleRate, sensorA, sensorB, sensorC, sensorD, sensorJ, sensorK))
except:
    print("Steering or Kill Switch Thread Failed to Start")
    

currentThrottle = getStop()


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
            if currentThrottle < motorMax:
                currentThrottle += resp 
                move = True
            screen.addstr(0, 0, 'up   ' + str(currentThrottle))       
        elif char == curses.KEY_DOWN:
            if currentThrottle > motorMin:
                currentThrottle -= resp 
                move = True
            screen.addstr(0, 0, 'down    ' + str(currentThrottle))
        elif char == ord('\n'):
            currentThrottle = motorMin 
            move = True
            screen.addstr(0, 0, 'Stoppp    ' + str(currentThrottle))     
        elif 48 <= char and char <= 57:
            index = int(char) - 48
            currentThrottle = speedOptions[index] 
            move = True
            screen.addstr(0, 0, 'Speed Set at    ' + str(index) + ":  "+ str(currentThrottle))
        elif char == ord('p'):
            if(320 < preferredSpeed < 440):
                currentThrottle = preferredSpeed
            else:
            currentThrottle = 340
            move = True
            screen.addstr(0, 0, 'Speed Set at    ' + str(currentThrottle))
	    elif char == ord('s'):
            # stop everything 
            currentThrottle = getStop() 
            current_turn_position  = getCenter()
            screen.addstr(0, 0, 'up    ' + str(currentThrottle) + ' and down ' + str(current_turn_position))       
            move = True
        
        if move:
            pwm.set_pwm(1, 0, currentThrottle)
finally:
    # shut down cleanly
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()
    pwm.set_pwm(1, 0, motorMin)
    time.sleep(1)

