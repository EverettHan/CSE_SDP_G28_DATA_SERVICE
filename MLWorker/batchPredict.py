import os
import keras
import numpy
import requests
import sys
import tensorflow
import time

from PIL import Image
from skimage import transform
from io import BytesIO
from numpy import vstack

def worker_loop(hostname, model):
    # First step: Check for work from the data service
    work_check = requests.post(hostname + "/requestwork")
    work_check = work_check.json()
    classification_id = work_check['classification_id']

    # This is the do nothing and wait case.
    if classification_id == None:
        return False

    # If we've been assigned work we move onto step 2

    # Get the image assigned to the classification request
    image_response = requests.get(hostname + "/getimage?classification_id={}".format(classification_id))
    image = Image.open(BytesIO(image_response.content))
    image = numpy.array(image).astype('float32')/255
    image = transform.resize(image, (218, 178, 3)) # TODO - parameterize this image resize
    image = numpy.expand_dims(image, axis=0)

    # Make a prediction on the image using the model
    pred = model.predict(image)[0, 0]

    # Post the prediction back to the data service
    response_dict = dict()
    response_dict['classification_id'] = classification_id
    response_dict['assigned_on'] = work_check['assigned_on']
    response_dict['errors'] = "" # TODO - Figure out where keras will spit out errors

    # Using the result of the prediction assing a classification
    # TODO - In the future these possibilities should be fetchable from the data service
    # if round(pred) == 1:
    #     response_dict['classification'] = "covid-19"
    # else:
    #     response_dict['classification'] = "not covid-19"


    messageReturn = "{ \"covidPred\": " + "{:.3f}".format(pred) + " }"
    response_dict['classification'] = messageReturn

    # Report the predicted classification back to the data service
    requests.post(hostname + "/reportclassification", json=response_dict)

    # Return true to denote that there was previously work assigned to the worker instance
    # and there may still be more images to classify
    return True

def decode_predictions(predictions, top=3):
    """ Interpret the predictions
    
    Arguments:
        predictions [[float]] -- predictions made by the model
    Yields:
        generator([float]) -- sorted result
    """
    for pred in predictions:
        indexes = argpartition(pred, -top)[-top:]
        indexes = indexes[argsort(-pred[indexes])]
        preds = list()
        for i in xrange(top):
            preds.append((indexes[i], pred[indexes[i]]))
        yield preds


def worker_loop2(hostname, model):
    # First step: Check for work from the data service
    work_list = requests.post(hostname + "/requestjobs")
    work_list = work_list.json()

    # This is the do nothing and wait case.
    if len(work_list) == 0:
        return False

    image_IDs = []
    assigned_IDs = []
    batch = None
    for aReq in work_list:
        classification_id = aReq['classification_id']
        assigned_id = aReq['assigned_on']

        # Get the image assigned to the classification request
        image_response = requests.get(hostname + "/getimage?classification_id={}".format(classification_id))
        image = Image.open(BytesIO(image_response.content))
        image = numpy.array(image).astype('float32')/255
        image = transform.resize(image, (218, 178, 3)) # TODO - parameterize this image resize
        image = numpy.expand_dims(image, axis=0)

        if batch is None:
            batch = image
        else:
            batch = vstack([batch, image])
        image_IDs.append(classification_id)    
        assigned_IDs.append(assigned_id)

    # Make prediction on the images using the model
    preds = model.predict(batch)
    #results = decode_predictions(preds)

    for (image_id, assigned_id, pred) in zip (image_IDs, assigned_IDs, preds):  
         # Post the prediction back to the data service
        response_dict = dict()
        response_dict['classification_id'] = image_id
        response_dict['assigned_on'] = assigned_id
        response_dict['errors'] = "" # TODO - Figure out where keras will spit out errors

        prob = pred[0] 
        messageReturn = "{ \"covidPred\": " + "{:.3f}".format(float(prob)) + " }"
        response_dict['classification'] = messageReturn
           

        # Report the predicted classification back to the data service
        requests.post(hostname + "/reportclassification", json=response_dict)
          

    # Return true to denote that there was previously work assigned to the worker instance
    # and there may still be more images to classify
    return True

if __name__ == "__main__":
    arguments = sys.argv[1:] # ignore __init__.py argument
    argc = len(arguments)

    hostname = "http://127.0.0.1:8000"
    model = "covid_fine_tuned.h5"
    interval = 15.0

    for i in range(0,len(arguments),2):
        parameter = arguments[i]
        if i+1 >= len(arguments):
            raise Exception("No value passed for parameter {}", parameter)

        value = arguments[i+1]
        
        if parameter == "--hostname":
            hostname = value
        elif parameter == "--model":
            model = value
        elif parameter == "--retry_interval":
            interval = float(value)

    model = keras.models.load_model(model)

    # The loop of the worker instance
    while True:
        work_check = worker_loop2(hostname, model)
        if not work_check:
            time.sleep(interval)

