import math
import turtle
import time
import sys

SECOND = 1 # How long a second is in the model
METER = 5 # How long a meter is in the model

LENGTH = 40
RADIUS = 19.10
HEIGHT = 2
PERIMETER = 200

DIAGONAL = math.sqrt(LENGTH * LENGTH + RADIUS * RADIUS) # Already in Meters
CORNER_ANGLE = math.atan(LENGTH / RADIUS)

LAP_SPLIT = 40

MAX_PAN_SPEED = 11.5 # @ 4.8 V is 110 RPM so 110/60 RPS so 11.5 rad/s
MAX_TILT_ANGLE = math.pi

NOISE_CONSTANT = 0.0383
NOISE_COEFFICIENT = 0.994

STEPS_PER_SECOND = 25

PRINT_SPLITS = False

MAX_ROTATION = ((math.pi * 2) - .5)

class Track:

    def __init__(self, perimeter, radius=-1, length=-1):
        self.perimeter = perimeter
        if((radius == -1 and length == -1) or (radius != -1 and length != -1)):
            raise EnvironmentError("You need to enter either only a radius or onlya length to proceed.")
        elif(radius == -1):
            self.length = length
            self.radius = (perimeter - (length*2)) / math.pi
        else:
            self.radius = radius
            self.length = (perimeter - (math.pi * 2 * radius)) / 2
    
    def getPerimeter(self):
        return self.perimeter
    
    def getLength(self):
        return self.length

    def getRadius(self):
        return self.radius

        

class Motor:

    def __init__(self, laser, maxPanVoltage=5, maxTiltVoltage=5, maxVoltage=-1):
        self.pan = 0
        self.laser = laser
        self.setupTurtle()
        self.startTime = -1
        self.elapsedTime = 0
        self.lap_split = 0
        if(maxVoltage != -1):
            self.maxPanVoltage = maxVoltage
            self.maxTiltVoltage = maxVoltage
        else:
            self.maxPanVoltage = maxPanVoltage
            self.maxTiltVoltage = maxTiltVoltage

    def setupTurtle(self):
        self.laser.penup()
        self.laser.shape("circle")
        self.laser.goto(RADIUS, 0)
        self.laser.pendown()

    def reset(self):
        # Rotation MAX_ROTATION Backwards
        # at maximum speed for the amount of time to reach the starting position
        self.__init__(self.laser)

    def makeLap(self):
        print("Starting at an angle of 0 rads")
        while self.pan <= math.pi * 2:
            startExecution = time.time()
            incr = self.calculateIncrement()
            self.panLeft(incr)
            print(self.calculatePanVoltage())
            print(self.calculateTiltVoltage())
            if PRINT_SPLITS:
                self.printPosition(self.calculateDistance())
            totalExecution = time.time() - startExecution
            sleepTime = 1/STEPS_PER_SECOND - totalExecution
            if(sleepTime < 0):
                sleepTime = 0
            time.sleep(sleepTime)
        print("Time Taken before Revert:", self.elapsedTime)

    def reverseToStart(self):
        timeLeft = LAP_SPLIT - self.elapsedTime
        print(timeLeft)
        numSteps = timeLeft * STEPS_PER_SECOND
        angle = MAX_ROTATION / numSteps
        print("Angle to Move", angle)
        while self.pan > 0:
            startExecution = time.time()
            self.panRight(angle)
            print(self.calculatePanVoltage())
            print(self.calculateTiltVoltage())
            totalExecution = time.time() - startExecution
            sleepTime = 1/STEPS_PER_SECOND - totalExecution
            if(sleepTime < 0):
                sleepTime = 0
            time.sleep(sleepTime)
        print("Time Taken:", self.elapsedTime)
        return LAP_SPLIT - self.elapsedTime
        

    def keepTime(self):
        if(self.startTime == -1):
            self.startTime = time.time()
        else:
            self.elapsedTime = time.time() - self.startTime

    def getTilt(self):
        distance = self.calculateDistance()
        return math.atan(distance/HEIGHT)

    def calculateIncrement(self):
        isFirstTurn = self.pan >= 0 and self.pan < math.pi
        angleToHomeStretchCorner = 2 * math.pi - CORNER_ANGLE
        isSecondTurn = self.pan >= math.pi + CORNER_ANGLE and self.pan <= angleToHomeStretchCorner

        if(isFirstTurn):
            return PERIMETER / ( RADIUS * LAP_SPLIT * STEPS_PER_SECOND)
        elif (isSecondTurn):
            return PERIMETER * (math.pi - 2 * CORNER_ANGLE) / (math.pi * RADIUS * LAP_SPLIT * STEPS_PER_SECOND)
        else:
            rho = self.pan - math.pi 
            if self.pan > math.pi * 3 / 2:
                rho = math.pi * 2 - self.pan
            return math.atan( math.tan(rho) + (PERIMETER / (LAP_SPLIT * STEPS_PER_SECOND * RADIUS))) - rho
    
    def calculatePanVoltage(self):
        stationary = maxDirectionalSpeed = self.maxPanVoltage / 2
        return stationary + self.calculateIncrement() * STEPS_PER_SECOND * maxDirectionalSpeed / MAX_PAN_SPEED
    
    def calculateTiltVoltage(self):
        maxDirectionalTilt = MAX_TILT_ANGLE/2
        middleVoltage = maxDirectionalVoltage = self.maxTiltVoltage / 2
        return middleVoltage + self.getTilt() * middleVoltage / maxDirectionalTilt

    def panLeft(self, increment):
        self.pan += increment
        self.moveLaser()
        self.keepTime()

    def panRight(self, increment):
        self.pan -= increment
        self.moveLaser()
        self.keepTime()

    def moveLaser(self):
        distance = self.calculateDistance()
        xPosition = distance * math.cos(self.pan)
        yPosition = distance * math.sin(self.pan)
        self.laser.goto(xPosition, yPosition)

    def calculateDistance(self):
        
        isFirstTurn = self.pan >= 0 and self.pan <= math.pi
        isBackStretch = self.pan > math.pi and self.pan <= math.pi + CORNER_ANGLE
        angleToHomeStretchCorner = 2 * math.pi - CORNER_ANGLE
        isSecondTurn = self.pan > math.pi + CORNER_ANGLE and self.pan <= angleToHomeStretchCorner
        
        distanceToRail = RADIUS
        
        if isFirstTurn:
            distanceToRail = RADIUS
        elif isBackStretch:
            distanceToRail = self.calculateBackStretch()
        elif isSecondTurn:
            distanceToRail = self.calculateSecondTurn()
        else:
            distanceToRail = self.calculateHomeStretch()

        return distanceToRail
    
    def calculateBackStretch(self):
        beta = (math.pi/2) - (self.pan - math.pi)
        return (RADIUS / math.sin(beta))
    
    def calculateSecondTurn(self):
        squares = (RADIUS * RADIUS) + (LENGTH * LENGTH)
        theta = self.pan - math.pi / 2
        arcSineSegment = math.asin(LENGTH * math.sin(theta) / RADIUS)
        cosSegment = 2 * RADIUS * LENGTH * math.cos(arcSineSegment - theta)
        discrim = squares - cosSegment
        return math.sqrt(discrim)
    
    def calculateHomeStretch(self):
        beta = (math.pi/2) - (2 * math.pi - self.pan)
        return (RADIUS / math.sin(beta))

    def printPosition(self, distance):
        tolerance = 0.05
        positions = [math.pi, math.pi + CORNER_ANGLE, math.pi * 2 - CORNER_ANGLE, math.pi * 2]
        for pos in positions:
            if(math.isclose(self.pan, pos, abs_tol=tolerance)):
                print("----------------------------")
                print("Pan Angle is", self.pan, "radians and", math.degrees(self.pan), "degrees")
                # print("Distance to lane 1 is", distance / METER, "meters")
                # tilt = self.getTilt(distance)
                # print("Tilt Angle is", tilt, "radians and", math.degrees(tilt), "degrees")
                print("Time Taken is", self.elapsedTime, "seconds")
                print("----------------------------")


def main(lap=LAP_SPLIT, trackSize=PERIMETER, stepsPerSecond=STEPS_PER_SECOND, diameter=38.2):

    window = turtle.Screen()
    window.bgcolor = "Salmon"
    window.title("Race Pace Systems Model")
    laser = turtle.Turtle()
    
    piMotor = Motor(laser)
    piMotor.makeLap()
        
    
    window.exitonclick()
    


if __name__ == "__main__":
    print(sys.argv)
    args = sys.argv[1:]

    print(args)
    if(args):
        HEIGHT = float(args[0])
        PERIMETER = float(args[1])
        LAP_SPLIT = (float(args[2]) * NOISE_COEFFICIENT + NOISE_CONSTANT)
        type = args[3]
        if(type == '-r'):
            RADIUS = float(args[4])
            LENGTH = (PERIMETER - (math.pi * 2 * RADIUS)) / 2
        elif(type == '-l'):
            LENGTH = float(args[4])
            RADIUS = (PERIMETER - (LENGTH*2)) / (2 * math.pi)
        else:
            raise Exception("Please Enter a Radius or Length with -r or -l")
        DIAGONAL = math.sqrt(LENGTH * LENGTH + RADIUS * RADIUS) # Already in Meters
        CORNER_ANGLE = math.atan(LENGTH / RADIUS)


        HEIGHT *= METER
        PERIMETER *= METER
        RADIUS *= METER
        LENGTH *= METER
        DIAGONAL *= METER
    else:
        print("Usage:")
        print("Print Usage")
        print("Using Default Values for now")

    print("Starting with values:")
    print("Length:", LENGTH / METER)
    print("Radius:", RADIUS / METER)
    print("Height:", HEIGHT / METER)
    print("Diagonal:", DIAGONAL / METER)
    print("Corner Angle", CORNER_ANGLE)
    print("Steps per Second", STEPS_PER_SECOND)
    input("Begin Simulation: (Press Enter)")

    main()
    

