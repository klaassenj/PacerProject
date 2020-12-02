import os
import zipfile
import time
import tensorflow as tf
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras import layers
from tensorflow.keras import Model
import numpy as np
import random
from tensorflow.keras.preprocessing.image import img_to_array, load_img

base_dir = './MLData'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
image_size = 100

# Directory with our training left pictures
train_lefts_dir = os.path.join(train_dir, 'Left')

# Directory with our training right pictures
train_rights_dir = os.path.join(train_dir, 'Right')

# Directory with our training straight pictures
train_straights_dir = os.path.join(train_dir, 'Straight')

# Directory with our validation left pictures
validation_lefts_dir = os.path.join(validation_dir, 'Left')

# Directory with our validation right pictures
validation_rights_dir = os.path.join(validation_dir, 'Right')

# Directory with our validation straight pictures
validation_straights_dir = os.path.join(validation_dir, 'Straight')

train_left_fnames = os.listdir(train_lefts_dir)
print(train_left_fnames[:10])

train_right_fnames = os.listdir(train_rights_dir)
train_right_fnames.sort()
print(train_right_fnames[:10])

train_straight_fnames = os.listdir(train_straights_dir)
train_straight_fnames.sort()
print(train_straight_fnames[:10])

print('total training left images:', len(os.listdir(train_lefts_dir)))
print('total training right images:', len(os.listdir(train_rights_dir)))
print('total training straight images:', len(os.listdir(train_straights_dir)))
print('total validation left images:', len(os.listdir(validation_lefts_dir)))
print('total validation right images:', len(os.listdir(validation_rights_dir)))
print('total training straight images:', len(os.listdir(validation_straights_dir)))


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

from tensorflow.keras.preprocessing.image import ImageDataGenerator

# All images will be rescaled by 1./255
train_datagen = ImageDataGenerator(rescale=1./255)
val_datagen = ImageDataGenerator(rescale=1./255)

# Flow training images in batches of 20 using train_datagen generator
train_generator = train_datagen.flow_from_directory(
        train_dir,  # This is the source directory for training images
        target_size=(image_size, image_size),  # All images will be resized to image_size
        batch_size=128,
        # Since we use binary_crossentropy loss, we need binary labels
        class_mode='categorical')

# Flow validation images in batches of 20 using val_datagen generator
validation_generator = val_datagen.flow_from_directory(
        validation_dir,
        target_size=(image_size, image_size),
        batch_size=64,
        class_mode='categorical')

history = model.fit_generator(
      train_generator,
      steps_per_epoch=100,  # 2000 images = batch_size * steps
      epochs=25,
      validation_data=validation_generator,
      validation_steps=50,  # 1000 images = batch_size * steps
      verbose=2)

model.save_weights("weightsV2/weightsV2")

uncompiledModel = Model(img_input, output)


# Let's prepare a random input image of a left or right from the training set.
left_img_files = [os.path.join(train_lefts_dir, f) for f in train_left_fnames]
right_img_files = [os.path.join(train_rights_dir, f) for f in train_right_fnames]
straight_img_files = [os.path.join(train_straights_dir, f) for f in train_straight_fnames]

# LEFT --------------
    
print("Compiled")
for i in range(10):
    img_path = random.choice(left_img_files)
    img = load_img(img_path, target_size=(image_size, image_size))  # this is a PIL image
    x = img_to_array(img)  # Numpy array with shape (150, 150, 3)
    x = x.reshape((1,) + x.shape)  # Numpy array with shape (1, 150, 150, 3)
    x /= 255
    start = time.time()
    results = model(x, training=False)
    timeTaken = time.time() - start
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


# RIGHT --------------

print("Compiled")
for i in range(10):
    img_path = random.choice(right_img_files)
    img = load_img(img_path, target_size=(image_size, image_size))  # this is a PIL image
    x = img_to_array(img)  # Numpy array with shape (150, 150, 3)
    x = x.reshape((1,) + x.shape)  # Numpy array with shape (1, 150, 150, 3)
    # Rescale by 1/255
    x /= 255
    start = time.time()
    results = model(x, training=False)
    timeTaken = time.time() - start
    print(results, timeTaken)


# STRAIGHT ---------------------

print("Compiled")
for i in range(10):
    img_path = random.choice(straight_img_files)
    img = load_img(img_path, target_size=(image_size, image_size))  # this is a PIL image
    x = img_to_array(img)  # Numpy array with shape (150, 150, 3)
    x = x.reshape((1,) + x.shape)  # Numpy array with shape (1, 150, 150, 3)
    # Rescale by 1/255
    x /= 255
    start = time.time()
    results = model(x, training=False)
    timeTaken = time.time() - start
    print(results, timeTaken)

# Retrieve a list of accuracy results on training and validation data
# sets for each training epoch
acc = history.history['acc']
val_acc = history.history['val_acc']

# Retrieve a list of list results on training and validation data
# sets for each training epoch
loss = history.history['loss']
val_loss = history.history['val_loss']

# Get number of epochs
epochs = range(len(acc))

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# Plot training and validation accuracy per epoch
plt.plot(epochs, acc)
plt.plot(epochs, val_acc)
plt.title('Training and validation accuracy')

plt.figure()

# Plot training and validation loss per epoch
plt.plot(epochs, loss)
plt.plot(epochs, val_loss)
plt.title('Training and validation loss')

plt.show()
