# -*- coding: utf-8 -*-
"""RIB_Bangkit_2022_test_drive

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rcjA7jJII1IK7wDXMUT4ap31n6vnxGBc
"""

# !pip3 install keras-visualizer

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import pathlib
import os
import librosa
import json

from tensorflow.keras import layers
from tensorflow.keras import models
from sklearn.model_selection import train_test_split
from IPython import display
from keras_visualizer import visualizer

from google.colab import drive
drive.mount('/content/drive')

"""cd /content/drive/MyDrive/BANGKIT

!unzip /content/drive/MyDrive/dikeluarin_fixbgt.zip
"""

data_dir = pathlib.Path('/content/drive/MyDrive/BANGKIT/AnggotaTubuhPart1')
commands = np.array(tf.io.gfile.listdir(str(data_dir)))
print('Commands:', commands)

filename = tf.io.gfile.glob(str(data_dir) + '/*/*')
filename = tf.random.shuffle(filename)
num_samples = len(filename)
print("Number of total axample:", num_samples)
print("Number of examples per labes:", len(tf.io.gfile.listdir(str(data_dir/commands[0]))))
print("Example file tentor:", filename[0])

#Pre Processing Dataset
def preprocess_dataset(dataset, json_path, mfcc_coef=12, fft_length=2048, hop_length=512):

    data = {"mapping": [], "labels": [], "mfcc": [], "files": []}
    count=0
    
    for num_dir, (path_dir, name_dir, filename) in enumerate(os.walk(dataset)):
       
        if path_dir is not dataset:       
            labeling = path_dir.split("/")[-2:]
            data["mapping"].append(labeling)
            print("\nProcessing: '{}'".format(labeling))

            for f in filename:
                file_path = os.path.join(path_dir, f)
                signal, rate = librosa.load(file_path)
                if len(signal) >= 22050: 
                    signal = signal[:22050]            
                    MFCCs = librosa.feature.mfcc(signal, rate, n_mfcc=mfcc_coef, n_fft=fft_length,
                                                    hop_length=hop_length)
                    count=count+1
                    data["mfcc"].append(MFCCs.T.tolist())
                    data["labels"].append(num_dir-1)
                    data["files"].append(file_path)
                    print(str(count)+" {}: {}".format(file_path, num_dir-1))

    with open(json_path, "w") as fp:
        json.dump(data, fp, indent=4)

#labelling
preprocess_dataset('/content/drive/MyDrive/BANGKIT/AnggotaTubuhPart1', 'AnggotaTubuh.json')

#Parameter
DATA_PATH = "AnggotaTubuh.json"
EPOCHS = 100
BATCH_SIZE = 10
PATIENCE = 10
LEARNING_RATE = 0.0001

def prepare_dataset(data_path):
    x, y = load_data(data_path)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)
    x_train, x_validation, y_train, y_validation = train_test_split(x_train, y_train, test_size=0.1)

    x_train = x_train[..., np.newaxis]
    x_test = x_test[..., np.newaxis]
    x_validation = x_validation[..., np.newaxis]

    return x_train, y_train, x_validation, y_validation, x_test, y_test

def load_data(data_path):
    with open(data_path, "r") as fp:
        data = json.load(fp)

    x = np.array(data["mfcc"])
    y = np.array(data["labels"])
    print("Training sets loaded!")
    return x, y

def build_model(input_shape, learning_rate=LEARNING_RATE):
    
    # build network architecture using convolutional layers
    model = tf.keras.models.Sequential()

    # 1st conv layer
    model.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape, padding="same"))
    #model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.MaxPooling2D((3, 3), strides=(2,2), padding='same'))

    # 2nd conv layer
    model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding="same"))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.MaxPooling2D(3, 3))

    # flatten output and feed into dense layer
    model.add(tf.keras.layers.Flatten())
    #model.add(tf.keras.layers.Dense(128, activation='relu'))
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    tf.keras.layers.Dropout(0.1)

    # softmax output layer
    model.add(tf.keras.layers.Dense(10, activation='softmax'))

    # compile model
    model.compile(optimizer=tf.optimizers.Adam(learning_rate=learning_rate),
                  loss='sparse_categorical_crossentropy',
                  metrics=["accuracy"])

    # print model parameters on console
    model.summary()

    return model

def train(model, epochs, batch_size, patience, X_train, y_train, X_validation, y_validation):
    
    earlystop_callback = tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", min_delta=0.001, patience=patience)  

    history = model.fit(X_train,
                        y_train,
                        epochs=epochs,
                        batch_size=batch_size,
                        validation_data=(X_validation, y_validation),
                        callbacks=[earlystop_callback])
    return history

def plot_history(history):
    
    fig, axs = plt.subplots(2)

    plt.figure(figsize=(5,10))

    # create accuracy subplot
    axs[0].plot(history.history["accuracy"], label="accuracy")
    axs[0].plot(history.history['val_accuracy'], label="val_accuracy")
    axs[0].set_ylabel("Accuracy")
    axs[0].legend(loc="lower right")
    axs[0].set_title("Accuracy evaluation")

    # create loss subplot
    axs[1].plot(history.history["loss"], label="loss")
    axs[1].plot(history.history['val_loss'], label="val_loss")
    axs[1].set_xlabel("Epoch")
    axs[1].set_ylabel("Loss")
    axs[1].legend(loc="upper right")
    axs[1].set_title("Loss evaluation")

    

    plt.show()

x_train, y_train, x_validation, y_validation, x_test, y_test = prepare_dataset(DATA_PATH)

input_shape = (x_train.shape[1], x_train.shape[2], 1)
model = build_model(input_shape, learning_rate=LEARNING_RATE)

print(x_train.shape)

print(input_shape)

history = train(model, EPOCHS, BATCH_SIZE, PATIENCE, x_train, y_train, x_validation, y_validation)

plot_history(history)

test_loss, test_acc = model.evaluate(x_test, y_test)

test_loss

test_acc

model_name = 'AnggotaTubuh_4.h5'
model.save(model_name, save_format='h5')

#preprocess the input sample function
def preprocess(file_path, num_mfcc=12, n_fft=2048, hop_length=512):
        """Extract MFCCs from audio file.
        :param file_path (str): Path of audio file
        :param num_mfcc (int): # of coefficients to extract
        :param n_fft (int): Interval we consider to apply STFT. Measured in # of samples
        :param hop_length (int): Sliding window for STFT. Measured in # of samples
        :return MFCCs (ndarray): 2-dim array with MFCC data of shape (# time steps, # coefficients)
        """
        signal, sample_rate = librosa.load(file_path)

        if len(signal) >= 22050:
            # ensure consistency of the length of the signal
            signal = signal[:22050]

            # extract MFCCs
            MFCCs = librosa.feature.mfcc(signal, sample_rate, n_mfcc=num_mfcc, n_fft=n_fft,
                                         hop_length=hop_length)
        return MFCCs.T

loaded=tf.keras.models.load_model(model_name)

def predict(file_path):
       
        # extract MFCC
        MFCCs = preprocess(file_path)

        # we need a 4-dim array to feed to the model for prediction: (# samples, # time steps, # coefficients, 1)
        MFCCs = MFCCs[np.newaxis, ..., np.newaxis]

        # get the predicted label
        predictions = loaded.predict(MFCCs)

        return predictions

def prediksi(data_predict):
  print("Prediksi: \n")
  print("Pundak: "+str(data_predict[0,0]*100)+"%")
  print("Mata: "+str(data_predict[0,1]*100)+"%")
  print("perut: "+str(data_predict[0,2]*100)+"%")
  print("Pipi: "+str(data_predict[0,3]*100)+"%")
  print("Telinga: "+str(data_predict[0,4]*100)+"%")
  print("Gigi: "+str(data_predict[0,5]*100)+"%")
  print("Hidung: "+str(data_predict[0,6]*100)+"%")
  print("Jari: "+str(data_predict[0,7]*100)+"%")
  print("Lidah: "+str(data_predict[0,8]*100)+"%")
  print("Lutut: "+str(data_predict[0,9]*100)+"%")

data_predict = predict("/content/drive/MyDrive/BANGKIT/testing_hd.wav")
prediksi(data_predict)

data_predict = predict("/content/drive/MyDrive/BANGKIT/testing_gg.wav")
prediksi(data_predict)

data_predict = predict("/content/drive/MyDrive/BANGKIT/testing_ld.wav")
prediksi(data_predict)

data_predict = predict("/content/drive/MyDrive/BANGKIT/testing_mt.wav")
prediksi(data_predict)

data_predict = predict("/content/drive/MyDrive/BANGKIT/gigi_cadel.wav")
prediksi(data_predict)

data_predict = predict("/content/drive/MyDrive/BANGKIT/hidung_cadell.wav")
prediksi(data_predict)

data_predict = predict("/content/drive/MyDrive/BANGKIT/ld_cadel.wav")
prediksi(data_predict)

data_predict = predict("/content/drive/MyDrive/BANGKIT/mt_cadeell.wav")
prediksi(data_predict)