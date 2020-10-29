# Helps to figure out Max and Min values for ESC
# Using Right and Left Arrow keys, one can figure out Max and Min turn values
# Using Up and Down Arrow keys, one can settle on a speed limits suitable for the future task.
# Modified from http://www.codehaven.co.uk/using-arrow-keys-with-inputs-python/
# Author: Udayan Kumar
from __future__ import division
import curses
import time
# Import the PCA9685 module.
import pigpio
import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()


leftIR = 18
rightIR = 23

servoMin = 220
servoMax = 400

servoMiddle = (servoMax + servoMin) // 2

steeringPercentage = 0.05
steeringAmount = (servoMax - servoMin) * steeringPercentage

servoResponsiveOptions = [(x / 100) for x in range(3, 10)]
sampleRateOptions = [(x * 10) for x in range(6, 12)]
resp = 2

pulse_freq = 60
pwm.set_pwm_freq(pulse_freq)

pi = pigpio.pi()
 
def getStop():
    return servoMiddle

current_direction = getStop()


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
    while True:
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

