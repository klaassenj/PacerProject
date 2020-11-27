# Import Everything
import os
import zipfile
import time
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


# sess = tf.Session()
# graph = tf.get_default_graph()
# set_session(sess)



# Initalize Variables

# Camera
numCycles = 0
imageRatio = 1
imageWidth = 100
imageHeight = int(imageWidth * imageRatio)
image_size = imageWidth
capturesPerCycle = 40
cameraFramerate = 80

# Motor & Servo
motorMin = 300
motorMax = 400
speedOptions = [(x * 15 + 320) for x in range(0, 10)]
servoMin = 220
servoMax = 400
pulseFrequency = 50 # ESC takes 50 Hz
currentThrottle = 0
servoMiddle = (servoMax + servoMin) // 2
currentDirection = servoMiddle

# Load ML CNN Model
img_input = layers.Input(shape=(image_size, image_size, 3))
x = layers.Conv2D(16, 3, activation='relu')(img_input)
x = layers.MaxPooling2D(2)(x)
x = layers.Conv2D(32, 3, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)
x = layers.Conv2D(64, 3, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)
x = layers.Flatten()(x)
x = layers.Dense(512, activation='relu')(x)
output = layers.Dense(1, activation='sigmoid')(x)
model = Model(img_input, output)
model.summary()
# Compile Model
model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(lr=0.001),
              metrics=['acc'])
# Load Model
model.load_weights("weights")

converter = tf.lite.TFLiteConverter.from_saved_model("steeringModel")
tflite_model = converter.convert()


# Model is Ready

def setDirection(results):
    print("Setting Direction")

# Define Camera Function
def processImages():
    global numCycles
    global model
    global tflite_model
    global sess
    global graph
    stream = io.BytesIO()
    
    
    for i in range(capturesPerCycle):
        yield stream
        stream.seek(0)
        image = Image.open(stream)
        pixelArray = img_to_array(image) 
        pixelArray = pixelArray.reshape((1,) + pixelArray.shape)
        startTime = time.time()
        with graph.as_default():
            set_session(sess)
            results = tflite_model.predict(pixelArray)
            print("Camera Results Frame "+ str(i) + ":", results)
        predictTime = time.time()
        
        # Turn Wheels
        # pwm.set_pwm(0, 0, setDirection(results))
        stream.seek(0)
        stream.truncate()
        print("-------------------")
        print("Predict from Image:", predictTime - startTime)
        print("-------------------")
    numCycles += 1

import picamera
with picamera.PiCamera() as camera:
    print("Initialize Camera")
    camera.resolution = (imageWidth, imageHeight)
    camera.color_effects = (128, 128)
    camera.framerate = cameraFramerate
    print("Booting Camera...")
    time.sleep(2)
    print("Booted.")
    print("Starting Main Loop")
    try:
        while True:
            
            outputs = [io.BytesIO() for i in range(capturesPerCycle)]
            createOutputsTime = time.time()
            
            # Capture Image
            startTime = time.time()
            camera.capture_sequence(processImages(), 'jpeg', use_video_port=True)
            endTime = time.time()
            print(str(capturesPerCycle) + " images at ", capturesPerCycle / (endTime - startTime), "FPS")
            print("Camera Captures in:", endTime - startTime)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Completed")