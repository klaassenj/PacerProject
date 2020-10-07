greenLED = 16
blueLED = 12
infrared = 18

import pigpio
import time

pi = pigpio.pi()

data = []
if not pi.connected:
    exit();
else:
    while True:
        try:
            IR = pi.read(18)
            if(IR == 0):
                print('Left!')
            else:
                print('Straight!')
            time.sleep(1/60)
        except KeyboardInterrupt:
            print('Keyboard Interrupted. Stopping...')
            for datum in data:
                print(datum[0], datum[1])
            pi.stop()


def flashLEDs(pi):
    pi.write(12, 1)
    pi.write(16, 0)
    time.sleep(1)
    pi.write(12, 0)
    pi.write(16, 1)
    time.sleep(1)
