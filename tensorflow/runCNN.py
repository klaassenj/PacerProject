import os
import zipfile
from time import time
import tensorflow as tf
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras import layers
from tensorflow.keras import Model
from os import listdir
from os.path import isfile, join
import numpy as np
import random
from tensorflow.keras.preprocessing.image import img_to_array, load_img

image_size = 100

# Our input feature map is 150x150x3: 150x150 for the image pixels, and 3 for
# the three color channels: R, G, and B
img_input = layers.Input(shape=(image_size, image_size, 3))

# First convolution extracts 16 filters that are 3x3
# Convolution is followed by max-pooling layer with a 2x2 window
x = layers.Conv2D(8, 3, activation='relu')(img_input)
x = layers.MaxPooling2D(2)(x)

# Second convolution extracts 32 filters that are 3x3
# Convolution is followed by max-pooling layer with a 2x2 window
x = layers.Conv2D(16, 3, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)

# Third convolution extracts 64 filters that are 3x3
# Convolution is followed by max-pooling layer with a 2x2 window
x = layers.Conv2D(32, 3, activation='relu')(x)
x = layers.MaxPooling2D(2)(x)

# Flatten feature map to a 1-dim tensor so we can add fully connected layers
x = layers.Flatten()(x)

# Create a fully connected layer with ReLU activation and 512 hidden units
x = layers.Dense(64, activation='relu')(x)

# Create the output layer with numclasses nodes
output = layers.Dense(3, activation='softmax')(x)

# Create model:
# input = input feature map
# output = input feature map + stacked convolution/maxpooling layers + fully 
# connected layer + sigmoid output layer
model = Model(img_input, output)

model.summary()



model.compile(loss='categorical_crossentropy',
              optimizer=RMSprop(lr=0.001),
              metrics=['acc'])


model.save_weights("weightsV3/weightsV3")

uncompiledModel = Model(img_input, output)


# Let's prepare a random input image of a left or right from the training set.
from pathlib import Path
filenames = list(Path("./MLData").rglob("*.jpeg"))
print("# of Files", len(filenames))

print("Compiled")
for i in range(100):
    img_path = random.choice(filenames)
    img = load_img(img_path, target_size=(image_size, image_size))  # this is a PIL image
    x = img_to_array(img)  # Numpy array with shape (150, 150, 3)
    x = x.reshape((1,) + x.shape)  # Numpy array with shape (1, 150, 150, 3)
    x /= 255
    start = time()
    results = model(x, training=False)
    timeTaken = time() - start
    string = str(results)
    print(string)
    strings = string.split('[[')
    print(strings)
    strings = strings[1].split(']]')
    print(strings)
    strings = strings[0].split()
    print(strings)
    print([float(x) for x in strings])
    print(results, timeTaken)
    img.show()
    input("Next")
    input("Next")