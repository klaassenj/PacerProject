import time
import pigpio
import random
# Constants
LOWER_MOTOR = 18 # Connect servomotor to BCM 18
UPPER_MOTOR = 12 # Connet servomotor to BCM 12

# Set Pulse Width Range Values
MINIMUM_PWM = 500 
CENTER_PWM = 1500

# Tower Pro Servos rotate much further than Wave Share Servos, or at least these two I've used do
MAXIMUM_PWM_BLUE_TOWER_PRO = 2200 # This will stop the servo at 180 degrees of rotation
MAXIMUM_PWM_GREY_WAVE_SHARE = 2350 # This will stop the servo at 162 degrees of rotation

ANGLE_RANGE = 180

MILLISECONDS_PER_DEGREE_TOWER_PRO = (MAXIMUM_PWM_BLUE_TOWER_PRO - MINIMUM) / ANGLE_RANGE
MILLISECONDS_PER_DEGREE_WAVE_SHARE = (MAXIMUM_PWM_GREY_WAVE_SHARE - MINIMUM) / ANGLE_RANGE

TOWER_PRO = 'TP'
WAVE_SHARE = 'WS'

TOWER_PRO_RANGE = 202 # Degrees
WAVE_SHARE_RANGE = 162 # Degrees


# Create Pi object
pi = pigpio.pi()
if not pi.connected:
    exit(0)

def printCombinationInformation(lowerMotorType, upperMotorType):
    if(lowerMotorType == WAVE_SHARE and upperMotorType == WAVE_SHARE):
        print('This combination of motors only allows for up to 324 degrees of rotation')
    elif(lowerMotorType == TOWER_PRO and upperMotorType == WAVE_SHARE):
        print('This combination allows up to 342 degrees')
    else:
        print('Unknown Combination')
    

def getPulseWidthModulation(degrees, motorType=TOWER_PRO):
    ''' degrees : number from 0 to 180 '''
    if(motorType == TOWER_PRO):
        rate = MILLISECONDS_PER_DEGREE_TOWER_PRO
    elif(motorType == WAVE_SHARE):
        rate = MILLISECONDS_PER_DEGREE_WAVE_SHARE
    else:
        raise NotImplementedError('That Motor has not been implemented.')
    pulseWidth = 500 + degrees * rate   
    return pulseWidth

def move_to_angle(degrees, motorPin, motorType=TOWER_PRO):
    pi.set_servo_pulsewidth(motorPin, pulseWidth)

def combined_move_to_angle(degrees, lowerMotorPin, upperMotorPin, lowerMotorType, upperMotorType):
    printCombinationInformation(lowerMotorType, upperMotorType)
    if(degrees <= 180):
        move_to_angle(degrees, lowerMotorPin, lowerMotorType)
    elif(degrees > 180):
        move_to_angle(180, lowerMotorPin, lowerMotorType)
        move_to_angle(degrees - 180, upperMotorPin, upperMotorType)


pi.set_servo_pulsewidth(MOTOR, 0)

# Main Loop to keep execution running
try:
    while True:
        move_to_angle(-90)
        time.sleep(2)
        move_to_angle(0)
        time.sleep(2)
        move_to_angle(90)
        time.sleep(2)
except KeyboardInterrupt:
    pi.stop()