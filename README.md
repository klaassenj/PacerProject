# Pacer Project

## RC Pacer

Raspberry Pi powered Traxxas Slash follows the lines on the track to pace distance running athletes to Personal Bests.

## Notes for execution
1. Turn on the Traxxas Slash into mode 1 (Racing Mode - if Training Mode is selected, the steering extremes may be slightly different causing issues)
1. Run ```python3 calibrateMotor.py```
1. As you press the up arrow key, you should notice the throttle amount increase (starting at 300), then hear the electric motor noise. Once you feel it move, you can hit ```enter``` and the motor will shutdown again. Now the motor is calibrated and ready for use by the pacing algorithm
1. Navigate to tensorflow/ 
1. Run ```python3 pacery.py```
1. The front steering wheels should start to turn in response to the camera in the front.
1. There is a prompt on the command line for setting the speed. This will IMMEDIATELY be applied, so be careful of attached cables or if its on a table etc.

### Components:
- Raspberry Pi 4 B (Previously Pi 3 B+)
- Array of IR sensors
- Servo Driver board
- Traxxas Slash 2WD
- Long Life RC Car Battery
- 10000 mAh Portable Battery
- Pi Camera
- Bluetooth Speaker

#### ML Version
  Uses an Image Classification Machine Learning to make a decision on what angle to point the wheels based on the current image provided by the camera. Highest framerate currently 60 FPS using an overclocked Pi 4 B. The Pi 3 B+ maxxes out at around 41 FPS since it's processor is slightly slower and cannot overclock further.

#### IR Version (Archived)
  Uses an 8-sensor IR array to "see" the line underneath the car. Significantly affected by the level of sunlight and distance to the ground. Extremely unreliable.

## Laser Pacer (Likely Unsafe)
  A Raspberry Pi Project to create an Indoor Track Pacing System using Math, Lasers, and Servos.


