import requests
import numpy as np
import tensorflow as tf
import keras
from django.urls import path
from PIL import Image
from skimage import transform
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession


def load(filename):
   np_image = Image.open(filename)
   np_image = np.array(np_image).astype('float32')/255
   np_image = transform.resize(np_image, (218, 178, 3))
   np_image = np.expand_dims(np_image, axis=0)
   return np_image

def ProcessImage(image):
    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)

    model = keras.models.load_model(r'C:\Users\jaych\Documents\Senior Design\covid_fine_tuned.h5')
    img = load(dire)
    img.shape

    pred = model.predict(img)[0, 0]

    return round(pred)