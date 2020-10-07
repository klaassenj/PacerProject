greenLED = 16
blueLED = 12
leftIR = 18
rightIR = 23

import pigpio
import time

pi = pigpio.pi()

data = []
if not pi.connected:
    exit();
else:
    while True:
        try:
            leftSignal = pi.read(leftIR)
            if(leftSignal == 0):
                lightLED(pi, greenLED)
            elif (rightSignal == 0):
                lightLED(pi, blueLED)
            else:
                clearAll(pi)
            time.sleep(1/60)
        except KeyboardInterrupt:
            print('Keyboard Interrupted. Stopping...')
            for datum in data:
                print(datum[0], datum[1])
            pi.stop()


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
