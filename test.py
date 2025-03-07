dataDir = "E:/Work/NonoGram/"

import keras
import keras.utils
import tensorflow as tf
import numpy as np
import createDigitImage

def combine_data(train_data, train_labels, test_data, test_labels, extra_train_data, extra_test_data):
    train_data = np.concatenate([train_data, [image for image, label in extra_train_data]], axis=0)
    train_labels = np.concatenate([train_labels, [label for image, label in extra_train_data]], axis=0)
    test_data = np.concatenate([test_data, [image for image, label in extra_test_data]], axis=0)
    test_labels = np.concatenate([test_labels, [label for image, label in extra_test_data]], axis=0)
    return (train_data, train_labels, test_data, test_labels)

def use_only_generated_digits(extra_train_data, extra_test_data, train_count, test_count):
    train_data = np.reshape([data for (data, label) in extra_train_data], (train_count, 28, 28, 1))
    train_labels = [label for (data, label) in extra_train_data]
    test_data = np.reshape([data for (data, label) in extra_test_data], (test_count, 28, 28, 1))
    test_labels = [label for (data, label) in extra_test_data]
    return (train_data, train_labels, test_data, test_labels)


# Load the MNIST dataset from OpenCV (this loads pre-trained data)
# This is a convenient way to quickly get started with digit recognition.
def createDigitRecognizer():
    (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()
    '''
    # Load the MNIST dataset
    (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()
    
    # Preprocess the images
    train_images = train_images.astype('float32') / 255
    test_images = test_images.astype('float32') / 255

    extra_train_data = [createDigitImage.create_random_digit_image() for i in range(0, 5000)]
    extra_test_data = [createDigitImage.create_random_digit_image() for i in range(0, 1000)]

    # Reshape the images and add a channel dimension
    train_images = np.expand_dims(train_images, axis=-1)
    test_images = np.expand_dims(test_images, axis=-1)
    '''

    train_count = 40000
    test_count = 10000
    extra_train_data = [createDigitImage.create_random_digit_image() for i in range(0, train_count)]
    extra_test_data = [createDigitImage.create_random_digit_image() for i in range(0, test_count)]
    (train_data, train_labels, test_data, test_labels) = combine_data(train_images, train_labels, test_images, test_labels, extra_train_data, extra_test_data)
    train_data = np.reshape(train_data, (len(train_data), 28, 28, 1))
    test_data = np.reshape(test_data, (len(test_data), 28, 28, 1))

    # One-hot encode the labels
    train_labels = tf.keras.utils.to_categorical(train_labels)
    test_labels = tf.keras.utils.to_categorical(test_labels)
    
    # Build the CNN model
    model = keras.Sequential([
        keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Conv2D(64, (3, 3), activation='relu'),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.BatchNormalization(),
        keras.layers.Flatten(),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(64, activation='relu'),
        #keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(10, activation='softmax')
    ])
    
    # Compile the model
    model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
    
    # Train the model
    model.fit(train_data, train_labels, epochs=8, batch_size=64, validation_data=(test_data, test_labels))
    return model

import os

#import keras.saving
digitRecognizerModelFileName = f"{dataDir}/digitRecognizerMnist.keras"
digitRecognizer = createDigitRecognizer()
digitRecognizer.save(f"{dataDir}/digitRecognizerMnist.keras")