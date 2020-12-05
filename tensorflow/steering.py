'''
Author: Jason Klaassen

This AI Script is built for controlling an RC Car to trace along the lines
of a track. 

In terms of software you need

Python 3
Tensorflow ~1.14 (i.e. not 2.X)
Adafruit PCA9685 Library
Look at the imports


The Hardware setup is as follows

Raspberry Pi 3B+
Adafruit PCA9685 Servo Driver Board
Pi Camera (You may need a longer ribben cable than comes with the module)
10000 mAh Anker External Battery Pack
Traxxas 2WD Slash (Alternatively any RC Car that exposes the steering servo(s) 
    as well as the ESC for PWM control. These will generally be higher end >$200.)
Wireless Keyboard (You may need to visualize your directory structure if you 
    need to run commands without a screen or buy a small screen)

'''

from __future__ import division
print("Gathering Libraries...")
import os

import time
import _thread
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import optimizers
from tensorflow.keras.optimizers import schedules
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.models import load_model
from tensorflow.keras import layers
from tensorflow.keras import Model
import numpy as np
import random
import io
import time
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import time
# Import the PCA9685 module.
import Adafruit_PCA9685
import sys

# Initalize Variables

servoConstraint = 0
FPS = 40
args = sys.argv
if(len(args) > 1):
    servoConstraint = int(args[1])

# Camera
print("Initializing Camera Environment...")
numCycles = 0
imageRatio = 1
imageWidth = 100
imageHeight = int(imageWidth * imageRatio)
image_size = imageWidth

cameraFramerate = 80


# Motor & Servo
print("Initializing Motor & Servo...")
pwm = Adafruit_PCA9685.PCA9685()
motorMin = 300
motorMax = 450
speedOptions = [(x * 15 + 320) for x in range(0, 10)]
servoMin = 220
servoMax = 420
pulseFrequency = 50 # ESC takes 50 Hz
currentThrottle = 0
preferredSpeed = 425
servoMiddle = (servoMax + servoMin) // 2
directionLeft = ((servoMin + servoConstraint) + servoMiddle) // 2
directionRight = ((servoMax - servoConstraint) + servoMiddle) // 2
directionMiddleLeft = (directionLeft + servoMiddle) // 2
directionMiddleRight = (directionRight + servoMiddle) // 2
currentThrottle = 0
pwm.set_pwm_freq(pulseFrequency)


# Start Tensorflow Session
print("Starting Tensorflow...")
sess = tf.Session()
graph = tf.get_default_graph()
set_session(sess)


# Build ML CNN Model
print("Building Model...")
img_input = layers.Input(shape=(image_size, image_size, 3))
x = layers.Conv2D(8, 3, activation='relu')(img_input)
x = layers.MaxPooling2D(2)(x)
x = layers.Conv2D(16, 3, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)
x = layers.Conv2D(32, 3, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)
x = layers.Flatten()(x)
x = layers.Dense(64, activation='relu')(x)
output = layers.Dense(3, activation='relu')(x)
model = Model(img_input, output)
model.summary()


# Compile Model
print("Compiling Model...")
model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(lr=0.001),
              metrics=['acc'])


# Load Model
print("Loading Model...")
model.load_weights("weightsV1/weightsV1")


print("Mapping Keyboard Controls for ESC...")

# Register Keyboard presses


# TODO: Would like to change on keypress instead of on hitting enter
def controlMotor(speedOptions, preferredSpeed):
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(50)
    numbers = [str(x) for x in range(0, 10)]
    currentThrottle = motorMin
    lastThrottle = motorMin
    pwm.set_pwm(1, 0, motorMin)
    while True:
        string = input("Set Motor Throttle:")
        print(string)
        if string in numbers:
            print("Set Speed Option")
            currentThrottle = speedOptions[int(string)]
        elif string.lower() == 'p':
            print("Set Preferred Speed")
            currentThrottle = preferredSpeed
        elif string == '':
            print("Stoppp")
            currentThrottle = motorMin
        else:
            try:
                number = int(string)
                if number > motorMin and number < motorMax:
                    currentThrottle = number
                else:
                    print("Number is Out of Range.")
            except:
                print("Maybe this is a Pace?")
                try:
                    if(string.endswith('s')):
                        secondsPerLap = float(string[:-1])
                        metersPerSecond =  400 / secondsPerLap
                        # Convert from metersPerSecond to Throttle
                        print("Oops TODO m/s", metersPerSecond)

                except:
                    print("I am lost with that...")
        if(currentThrottle != lastThrottle):
            print("Setting New Throttle:", currentThrottle)
            pwm.set_pwm(1, 0, currentThrottle)
        lastThrottle = currentThrottle


# from pynput import keyboard
# def on_press(key):
#     global speedOptions
#     numbers = [str(x) for x in range(0, 10)]
#     stop = ['s', 'enter']
#     if key == keyboard.Key.esc:
#         print("Not Listening for Keys Anymore.")
#         pwm.set_pwm(1, 0, motorMin)
#         return False  # stop listener
#     try:
#         k = key.char  # single-char keys
#     except:
#         k = key.name  # other keys
#     print("Received Key:", k)
#     if k in numbers:  # keys of interest
#         # self.keys.append(k)  # store it in global-like variable
#         print("Setting Speed to", speedOptions[k])
#         pwm.set_pwm(1, 0, speedOptions[k])
#     if k in stop:
#         print("Setting Speed to", motorMin)
#         pwm.set_pwm(1, 0, motorMin)
#     time.sleep(0.1)

# listener = keyboard.Listener(on_press=on_press)
# listener.start()  # start to listen on a separate thread


print("Defining Functions...")

# Map Predictions to steering output
def processPrediction(predictionString):
    if predictionString == 'Straight':
        return servoMiddle
    if predictionString == 'Left':
        return directionLeft
    if predictionString == 'Right':
        return directionRight
    if predictionString == 'Straight-Left':
        return directionMiddleLeft
    if predictionString == 'Straight-Right':
        return directionMiddleRight


# Define Camera Function
def processImages():
    global model
    global sess
    global graph
    global pwm
    stream = io.BytesIO()
    
    for i in range(FPS):
        yield stream
        # Load Image from Camera
        stream.seek(0)
        image = Image.open(stream)
        pixelArray = img_to_array(image) 
        pixelArray = pixelArray.reshape((1,) + pixelArray.shape)
        # Predict with Model
        with graph.as_default():
            set_session(sess)
            results = model.predict(pixelArray)
            string = str(results)
            strings = string.split('[[')
            strings = strings[1].split(']]')
            strings = strings[0].split()
            numbers = [float(x) for x in strings]
            leftComponent = int(int(numbers[1] * 100) / 100)
            rightComponent = int(int(numbers[0] * 100) / 100)
            straightComponent = int(int(numbers[2] * 100) / 100)
            prediction = 'Straight'
            if(leftComponent > straightComponent):
                prediction = 'Left'
            if(rightComponent > leftComponent):
                prediction = 'Right'
            if leftComponent != 0 and straightComponent != 0:
                prediction = 'Straight-Left'
            if rightComponent != 0 and straightComponent != 0:
                prediction = 'Straight-Right'
        
        # Set Direction
        direction = processPrediction(prediction)
        # Turn Steering Servo
        pwm.set_pwm(0, 0, int(direction))
        # Reset Stream
        stream.seek(0)
        stream.truncate()

print("Loading Camera...")
import picamera
with picamera.PiCamera() as camera:
    camera.resolution = (imageWidth, imageHeight)
    camera.color_effects = (128, 128)
    camera.framerate = cameraFramerate
    print("Booting Camera...")
    time.sleep(2)
    print("Boot Complete...")
    try:
        print("Starting Motor...")
        _thread.start_new_thread(controlMotor, (speedOptions, preferredSpeed))
    except:
        print("Motor failed to Start...")
    print("Starting Main Loop...")
    try:
        while True:
            # Initialize Output Holders
            outputs = [io.BytesIO() for i in range(FPS)]
            # Capture Image
            camera.capture_sequence(processImages(), 'jpeg', use_video_port=True)
    except KeyboardInterrupt:
        print("Cleaning up and Shutting down...")
        pwm.set_pwm(1, 0, motorMin)
        pwm.set_pwm(0, 0, servoMiddle)
        time.sleep(1)
        print("Shutdown.")
