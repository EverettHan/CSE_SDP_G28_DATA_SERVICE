# The views of the classification web service

There will be a number of necessary operations to provide the necessary functionality. These operations are described as follows.

## CreateUser

### URL

```/createuser```

### Description

The create user operation will serve as a simple "hello world" endpoint. The following results will be given to the user depending on their input.

#### Request

The create user request requires a single POST parameter, "username".

#### Responses

The create user operation will respond with either a http response code of 200 if the user was successfully registered with the web service. Otherwise if the username provided already exists a http 400 error will be sent in response. If the request includes malformed data such as the absence of the "username" parameter or bad input to the value of the "username" parameter a http 400 response code will also be provided. More specific codes may be used later on to provide a more descriptive error response to the user.

## Login

### URL

```/login```

### Description

The login request will be added for future proofing the application. Currently there is no development plan to implement a secure login system although Django does come equipped with the necessary tools to implement such a system. Logging into the classification system is not necessary at this time.

### Request

The login request will be a http POST request. The login endpoint will take a "username" and a "password". The password field will be left as a place holder, but the parameter must be provided even if the field is left empty for every request.

### Response

If the provided "username" exists in the database the user will receive a http response code of 200. Otherwise the user will receive a http code of 400. 

## CreateDataset

### URL

```/createdataset```

### Description

The purpose of the classification system is to house multiple datasets and distribute the work required to train models using the images uploaded into system. This operation will be used to create new datasets as well as configure them with the proper parameters for the tensor flow library.

### Request

The create dataset request operation will be a http POST request

Post Parameters
- dataset_name (required): A string following the following regex ```python r"[A-Za-z\_\-]"```
- display_name (required): A prettier version of the dataset_name parameter. Feel free to use spaces here.
- description: A text field to house a paragraph or two of information about the purpose of the dataset.
- img_width: The minimum width of submitted images.
- img_height: The minimum height of submitted images.
- maintain_ratio: Force the ratio of the width and height to be maintained for image submissions. Forces image submissions to be pre-curated.

Request body:
A JSON string array denoting the classifications of any of the images within the dataset. **THE ORDER OF THE CLASSIFICATIONS MUST MATCH ALL MODEL OUTPUTS CREATED FOR THIS DATASET!**

Example:
```json
[
  "Foo",
  "Bar",
  "Some Third Label",
  "It could also be this label",
  "There are five labels"
]
```

### Response

If the dataset_name does not exist then the dataset should be accepted. Additional parameter checking for optional parameters will be expanded upon, but for now all that is necessary is to create a dataset which does not exist already.

- 200: dataset_name provided is unique and has not been previously used
- 400: otherwise

### Future requirements

Datasets must have an owner. Currently there are no plans to implement user sessions with the classification system. If sessions were a feature the user currently active within the session would be assigned as the owner of the dataset. However the dataset will be assigned to a generic "master" user for now. In the future the owner should be assigned to the user of the current session making the create dataset request.

## GetDatasetInfo

### URL

```/getdatasetinfo```

### Description

It will be necessary for the worker instances to get the dataset configuration in order to report the proper classifications. Therefore there will be an operation to get the configuration information of a particular dataset.

### Request

The get dataset info operation will use a http GET request.

Params:
- dataset_name: The name of the dataset entry's information request.

### Response

Header:
- description: A text field to house a paragraph or two of information about the purpose of the dataset.
- img_width: The minimum width of submitted images.
- img_height: The minimum height of submitted images.
- maintain_ration: Force the ratio of the width and height to be maintained for image submissions. Forces image submissions to be pre-curated.

Body:
JSON string array of classifications.

## DeleteDataset

### URL

```/deletedataset```

### Description

Operation to allow the deletion of the dataset from the database. This will result in a cascade of deletions which will remove all registered models as well as all previously classified requests and subsequent results from the database. Be careful when performing this operation.

### Request

Http POST request

Post Params
- dataset_name: The name of the dataset which will be deleted from the database.

### Response

If the dataset exists it will be deleted. Otherwise the operation will fail

- 200: dataset_name matches a dataset in the database and that dataset is deleted.
- 400: otherwise

### Future Requirements

Similar to the create dataset operation the owner of the dataset must be logged in. This will ensure that datasets are not deleted by malicious actors.

## SubmitModel

### URL

```/submitmodel```

### Description

The create model operation will allow users to submit pre-trained models for a particular dataset. This may be particularly useful for researchers who want to make their results available to the public without making the data used to the train the model available.

### Request

The submit model operation will be a http POST request

Post params:
- dataset_name: The dataset to which the model will be registered.
- model_name (optional): The name of the model to be registered. If not provided it will be named as "YYYY-MM-DD_dataset_name" where the date field is the day of submission for the model file.
- model_config: A JSON string with all necessary information for the tensor flow library to restore the model back to working order

Request body:
- The model file. This can range from a few megabytes to well over a hundred or hundreds.

### Response

This request will have the most stringent parameter verification. If the dataset_name provided does not match a dataset_name within the dataset table the request will fail. If the model_name provided in the request has already been used the request will fail. If the model config is not a valid JSON string the request will fail.

- 200: dataset_name is valid, model_name is valid if provided, and model_config is valid JSON
- 400: otherwise

### Future Development

This operation is tricky as it isn't clear who should have the ability to submit pre-trained models to the system. It would make sense to say that only the owner of the dataset should be able to submit pre-trained models to the system as they would theoretically be providing the most accurately trained model. Other users who want to suggest configurations for how best to train the model may do so without being the owner.

## GetModel

### URL

```/getmodel```

### Description

The get model operation will allow worker instances to download the model file for tensor flow as well as the JSON string config information necessary to restore the model.

### Request

Get model will use a http GET request

Params:
- model_id: The id of the model to download

### Response

Status:
- 200: The model exists
- 400: The model does not exist

Headers:
- config: JSON string defining how the model was configured

Body:
Model file

## DeleteModel

### URL

```/deletemodel```

### Description

Delete a model from the database. This will result in a cascade deletion of all classification requests / responses against it.

### Request

The delete model operation will use a http POST request.

Post params:
- model_id: The model_id of the model to be deleted.

### Response

- 200: Model deleted
- 400: Model does not exist

## Classify

### URL

```/classify```

### Description

One of the more powerful points of this system is the classification request. Users may upload an image to be classified against one of the models within the system. The user will be given a classification request ID to track their classification.

### Request

The classify operation will use a http POST request.

Post params:
- model_name: The name of the model the user wishes to classify against.

Request body:
The image to be classified.

### Response

There will be a few checks before registering the image with a classification id. Firstly, the model must exist within the database before the request is even considered. Secondly, the image must be processable by the Pillow library in python. If the image is not processed by Pillow the request will fail.

Status:
- 200: The model exists and the image was processable by the pillow library.
- 400: Either the model does not exist or the image was not compatible with the Pillow library

Body:
The classification request ID. The user will use this ID to in order to check the status or result of their request.

### Future Development

There should be a rate limit for the number of requests submitted by each of the users, or at least each of the IP addresses which makes a request. This will prevent one or a disproportionately small subset of users from monopolizing the computing power of the system.

## GetClassificationStatus

### URL

```/getclassificationstatus/```

### Description

Once a classification request has been made it is up to the number of worker instances to determine when the request will be fulfilled. Due to this non-deterministic behavior the classification requests will have one of three states. Pending, assigned, fulfilled. The fulfilled state will have any addition information required attached to it such as the classification, or any errors which may have occurred while classifying.

### Request

The get classification status operation will be a http GET request.

Get params:
- classification_id: The classification request id to check the status of.

### Response

Status:
- 200: The classification_id is valid and results exists
- 400: otherwise

Header:
- assigned_on: If the request is pending or fulfilled there will be a date assigned here.
- classification: String of classification result.
- classification_status: One of pending, assigned, or fulfilled.
- error_info: Any error output would show up here. A blank field denotes success.
- model_name: The name of the model the submitted image was classified against.

Body:
The image originally submitted for classification against the model.

### Future Developments

Who should be able to see these classifications? Perhaps there should be some sort of "role" system to prevent _anyone_ from being able to see all of the submitted requests.

## RequestWork

### URL

```/requestwork```

### Description

The beating heart of the classification system. This is where worker units will request work from the system. The assigning of work to worker instances will be a primitive first come first serve with some date time checks to reassign "dead in the water" operations. In other words if a classification request of a 4K image takes an hour and the worker instance assigned to perform that classification goes down then the request must be reassigned as _some point_.

### Request

The request work operation will be a http POST request.

Post params:
- N/A: Future expansion of this operation may allow worker instances to state their preferred dataset when requesting work. For now the worker instances will work with whatever they get.

### Response

Status:
- 200: POST request proceeded as intended. Unless the classification service crashes this should be the only code

Headers:
- classification_id: if null - no work to do, otherwise this will be the assigned classification_id
- assigned_on: Contains the datetime stamp of when the classification system assigned the request to a worker instance.
- model_name: TODO - In the future if this project is to be expanded on this parameter is to be used to link this request to the corresponding model it is attached to.

Body:
Json string

```json
{
  "classification_id": 12345,
  "assigned_on": "1970-01-01T00:00:00.000000"
}
```

### Future Development

In future the classification service may be expanded to support the distributed training of models. In that case this endpoint should also assign workers to training requests. The response given to the worker instance will have to change to determine which type of computation operation must be performed.

## GetImage

### URL

```/getimage```

### Description

During development it became apparent that there would have to be an additional endpoint added in order to download the image from the classification system. There could not be both a JSON response to the request as well as an included image. It would have been possible to convert the image into a base64 encoded string, but the resulting JSON would have become difficult to handle.

### Request

The getimage endpoint will use a HTTP GET request. There will be a single parameter, classification_id, to reference the image uploaded to the system.

### Response

An http response with the image included as the body of the response.

## ReportClassification

### URL

```/reportclassification```

### Description

This is the operation which allows worker instances to report their results wether they be erroneous or successful. This operation is currently the only operation with security in mind. A simple yet highly effective way to prevent false results from being reported is to require a proper dispatch_token for each request. When a request is assigned to a worker instance that request will be tagged with a newly generated dispatch_token that only the worker and the classification service know. No result may be reported without a dispatch_token.

### Request

The report classification operation will be a http POST request.

Params:
- classification: String representing classification originally defined in the dataset.
- classification_id: The assigned classification_id.
- assigned_on: The iso datetime string denoting when the request was assigned to a worker. Used to ensure that the worker assigned to this request is the worker reporting the result to this request.
- error_info: Any erroneous information. **Left empty for absence of errors**

```json
{
  "classification": "Some string",
  "classification_id": 12345,
  "assigned_on": "1970-01-01T00:00:00.000000",
  "error_info": ""
}
```

### Response

Status:
- 200: classification_id and dispatch_token are a match and the classification_id has not had a result submitted.
- 400: otherwise.


## getResults

### URL 
```/getresults```

### Description

This will return the result of a classification operation.

### Request

HTTP GET request

Params
- classification_id - The ID of the classification request created when a corresponding image was submitted to the system.
