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


model_name = 'AnggotaTubuh/'
loaded=tf.keras.models.load_model(model_name)



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



def predict(file_path):
       
        # extract MFCC
        MFCCs = preprocess(file_path)

        # we need a 4-dim array to feed to the model for prediction: (# samples, # time steps, # coefficients, 1)
        MFCCs = MFCCs[np.newaxis, ..., np.newaxis]

        # get the predicted label
        predictions = loaded.predict(MFCCs)

        return predictions


def prediksi(data_predict):
  hasil ={
  "Pundak":(data_predict[0,0]*100),
  "Mata":(data_predict[0,1]*100),
  "Perut":(data_predict[0,2]*100),
  "Pipi":(data_predict[0,3]*100),
  "Telinga":(data_predict[0,4]*100),
  "Gigi":(data_predict[0,5]*100),
  "Hidung":(data_predict[0,6]*100),
  "Jari":(data_predict[0,7]*100),
  "Lidah":(data_predict[0,8]*100),
  "Lutut":(data_predict[0,9]*100)}
  return hasil

def findmax(hasil):
  fin_max=max(hasil,key=hasil.get)
  return fin_max
