import RPi.GPIO as GPIO
import time
import math
import random

LOWER_MOTOR_PIN = 18
UPPER_MOTOR_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(LOWER_MOTOR_PIN, GPIO.OUT)
GPIO.setup(UPPER_MOTOR_PIN, GPIO.OUT)

lowerPWM = GPIO.PWM(LOWER_MOTOR_PIN, 50) # GPIO 18 for PWM with 50Hz
upperPWM = GPIO.PWM(UPPER_MOTOR_PIN, 50) # GPIO 12 for PWM with 50Hz
lowerPWM.start(5) # Initialization
upperPWM.start(5) # Initialization

# Initialized at 5 using 5V
RAD0 = (2.5, 2.5)
RADP2 = (6.8, 2.5)
RADP = (11.1, 2.5)
RAD3P2 = (11.1, 8.0)
RAD2P = (12.1, 12.5)
RAD7METERLEFT = (11.1, 12.3)

BASE_DUTY_CYCLE = 2.5
LOWER_MOTOR_DC_PER_RADIAN = 2.737   # L1: 2.737
UPPER_MOTOR_DC_PER_RADIAN = 3.501     # U1: 3.501
REVERSE_DUTY_CYCLE = 12.3
STEPS_PER_SECOND = 25
LAP_SPLIT = 40
REVERSING_TIME = 1
MAX_LOWER_DC = 11.1
FIRST_TURN = 1
BACK_STRETCH = 2
FAR_TURN = 3
HOME_STRETCH = 4
REVERSING = 5
ANGLE7MLEFT = .35146
REVERSE_ANGLE = 2 * math.pi - ANGLE7MLEFT


class Motor:

    def __init__(self, lowerMotor, upperMotor, 
                    baseDC=2.5, 
                    lowerMotorRate=LOWER_MOTOR_DC_PER_RADIAN,
                    upperMotorRate=UPPER_MOTOR_DC_PER_RADIAN,
                    reverseDC=REVERSE_DUTY_CYCLE,
                    maxLowerDC=MAX_LOWER_DC,
                    stepsPerSecond=STEPS_PER_SECOND,
                    lapSplit=LAP_SPLIT):
        self.lowerMotor = lowerMotor
        self.upperMotor = upperMotor
        self.baseDC = baseDC
        self.lowerMotorRate = lowerMotorRate
        self.upperMotorRate = upperMotorRate
        self.reverseDC = reverseDC
        self.stepsPerSecond = stepsPerSecond
        self.lapSplit = lapSplit
        self.maxLowerDC = maxLowerDC

        self.startTime = -1
        self.elapsedTime = 0
        #self.state

        print("Motor Specs ----------")
        print("Base DC", self.baseDC)
        print("Lower DC Rate", self.lowerMotorRate)
        print("Upper DC Rate", self.upperMotorRate)
        print("Reverse DC", self.reverseDC)
        print("--------------------")

    def slowCircle(self):
        angle = 0
        time_step = 1 / self.stepsPerSecond
        nextAngle = 2 * math.pi / (self.lapSplit * self.stepsPerSecond)
        while angle <= math.pi * 2:
            startTime = time.time()
            self.setMotors(angle)
            # angle  = random.randint(0, 614) / 100 --------- Moves to random angles between 0 and 2 pi
            angle += nextAngle
            
            self.keepTime()
            print("Angle in Radians", angle)
            if(angle >= REVERSE_ANGLE):
                break
            executionTime = time.time() - startTime
            time.sleep(time_step - executionTime)
        print("Time Taken:", self.elapsedTime)
        print("Time to reset:", self.lapSplit - self.elapsedTime)

    def keepTime(self):
        if(self.startTime == -1):
            self.startTime = time.time()
        self.elapsedTime = time.time() - self.startTime
    
    def reset(self):

        self.lowerMotor.ChangeDutyCycle(self.baseDC)
        self.upperMotor.ChangeDutyCycle(self.baseDC)
        sleepTime = self.lapSplit - self.elapsedTime
        if(sleepTime > 2):
            sleepTime = 2
        elif(sleepTime < 0):
            sleepTime = 0
        time.sleep(sleepTime)
        self.startTime = -1
        self.elapsedTime = 0


    def setMotors(self, radians):
        if(radians <= math.pi):
            dutyCycle = self.calculateDutyCycle('Lower', radians)
            self.lowerMotor.ChangeDutyCycle(dutyCycle)
        else:
            dutyCycle = self.calculateDutyCycle('Upper', radians - math.pi)
            if(dutyCycle > self.reverseDC):
                extra = dutyCycle - self.reverseDC
                self.lowerMotor.ChangeDutyCycle(self.maxLowerDC + extra)
            else:    
                self.upperMotor.ChangeDutyCycle(dutyCycle)

    def calculateDutyCycle(self, motorType, angle):
        result = self.baseDC
        if(motorType == 'Lower'):
            result += self.lowerMotorRate * angle
        elif(motorType == 'Upper'):
            result += self.upperMotorRate * angle
        else:
            print("Erroor!!! --- motorType is unknown choose either Lower or Upper")
        #print(motorType, result)
        return result

try:
    piMotor = Motor(lowerPWM, upperPWM, lapSplit=20)
    for i in range(2):
        piMotor.slowCircle()
        piMotor.reset()
except KeyboardInterrupt:
    pass
piMotor.reset()
lowerPWM.stop()
upperPWM.stop()
GPIO.cleanup()











# try:
#     # Start at 0 rads  ( Calibrated )
#     upperPWM.ChangeDutyCycle(2.5)
#     lowerPWM.ChangeDutyCycle(2.5)
#     print(2.5, 2.5)
#     time.sleep(3)

#     # Find pi/2 rads manually
#     lowerPWM.ChangeDutyCycle(6.8)
#     print(6.8, 2.5)
#     time.sleep(3)

#     # Find pi rads manually
#     lowerPWM.ChangeDutyCycle(11.1)
#     print(11.1, 2.5)
#     time.sleep(3)

#     # Find 3 * pi / 2 rads manually
#     upperPWM.ChangeDutyCycle(8.0)
#     print(11.1, 8.0)
#     time.sleep(3)

#     # Find Reverse Angle manually ( 7m before line )
#     lowerPWM.ChangeDutyCycle(11.1)
#     upperPWM.ChangeDutyCycle(12.3)
#     print(11.1, 12.3)
#     time.sleep(3)

#     # Find 2 pi manually
#     lowerPWM.ChangeDutyCycle(12.1)
#     upperPWM.ChangeDutyCycle(12.5)
#     print(12.0, 12.5)
#     time.sleep(3)
#     upperPWM.ChangeDutyCycle(2.5)
#     lowerPWM.ChangeDutyCycle(2.5)
#     time.sleep(3)
# except KeyboardInterrupt:
#     pass



