'''
Author: Jason Klaassen
12/2/2020
Image Sorter for Images Collected by tracing the lines on a track
This Sorter is not 100% Accurate. In its training using 
    https://teachablemachine.withgoogle.com/ it reached about 80% Accuracy.
    It will however save a lot of sorting time! Especially with 10000+ Sets of Images
    You can optionally go over the sort by hand and fix its mistakes to give more
    accurate data labels to the actual production Neural Net for better accuracy.

The Sorter will

The Sorter assumes you have a Folder with general a structure as follows

MLData
    | > Left
    | > Right
    | > Straight
    | > frame1.jpeg
    | > frame7.jpeg
    | > ...
    | > frame1023.jpeg

All images to be sorted must not be in any directories, but flat with each other

'''

import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import os
from os import listdir
from os.path import isfile, join
path = '../MLData'
filenames = [f for f in listdir(path) if isfile(join(path, f))]
print("# of Files: ", len(filenames))

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = tensorflow.keras.models.load_model('keras_model.h5')

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


for filename in filenames:
    # Replace this with the path to your image
    image = Image.open(path + filename)

    #resize the image to a 224x224 with the same strategy as in TM2:
    #resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

    #turn the image into a numpy array
    image_array = np.asarray(image)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)
    print(prediction)
    stringList = str(prediction).replace('[', '').replace(']', '').strip().split()
    floatList = [float(s) for s in stringList]
    prediction = 'Straight/'
    maxFloat = floatList[0]
    if(floatList[1] > floatList[0]):
        maxFloat = floatList[1]
        prediction = 'Left/'
    if(floatList[2] > maxFloat):
        prediction = 'Right/'
    print(prediction)
    print(filename)
    os.rename(path + filename, path + prediction + filename)