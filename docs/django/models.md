# Django models

The following describes the models created for the django python framework in order to accomplish the goal of creating a distributed system for classifying covid-19 images.

## Models

### User

```json
{
    "id": 12345,
    "username": "placeholder"
}
```

#### Description

- id: Primary key of the user entry
- username: The username of the user entry. This should behave as a psuedo primary key as there should never be any duplicates of this name. However nothing will be linked to the username just incase a user wants to change this value.

The user model is currently used as a placeholder. This will be explained later on for the dataset model definition.

### Dataset

```json
{
    "id": "[1-9][0-9]*",
    "name": "Short and to the point",
    "display_name": "A longer, prettier name",
    "description": "An in depth explanation of what the dataset is tracking",
    "img_width": 1920,
    "img_height": 1080,
    "maintain_ratio": true,
    "owner": "[0-9]"
}
```

#### Description

- id: Primary key
- name: The name of the dataset
- display_name: A longer, prettier display name
- description: Text field to hold as much information as the user would like to provide
- img_width: The minimum width of the images uploaded into the dataset
- img_height: The minimum height of the images uploaded into the dataset
- maintain_ratio: Boolean flag to the enforce the ration between the width and the height be maintained
- owner: A foreign key reference to the user who owns the dataset

The dataset will hold the descriptions of all of the datasets tracked by the classification webservice. There will only be one entry per dataset. All models linked to the dataset will reference this entry.

### Model

```json
{
    "id": "[1-9][0-9]*",
    "dataset": "[1-9][0-9]*",
    "uploaded_on": "date-time",
    "data": "TODO - Figure out what to do here"
}
```

#### Description

- id: Primary key
- dataset: Reference to the dataset entry
- uploaded_on: Date that the model was uploaded to the service
- data: TODO - Figure out how to store multiple megabyte blobs of data. HTTP requests can't pass this back and forth

Each of the models trained for each of the datasets will be stored in this database. Multiple models may exist for a single dataset. The date the model was uploaded will be kept on record.

### ClassificationRequest

```json
{
    "id": "[1-9][0-9]*",
    "fulfilled": true,
    "assigned_on": "datetime",
    "image": "TODO - What goes here"
}
```

#### Description

- id: Primary key. Auto generated id for the request
- fulfilled: boolean flag marking if this request was completed
- assigned_on: The date that this request was assigned to a worker. Also use this field to determine if a request should be re-assigned
- model: Foreign key reference to the model living in the database
- image: TODO - Figure out how to handle the image submission

The ComputeRequest will be the true power of the classification webservice. When a user submits a request for an image to be classified a ComputeRequest entry will be created. A worker instance will query the webservice in order to be assigned one of the unassigned requests.

### ClassificationResult

```json
{
    "id": "[1-9][0-9]*",
    "completed_on": "date time",
    "compute_request": 1455,
    "classification": "The result",
    "errors": "Description of errors"
}
```

#### Description

- id: The primary key of the result entry
- completed_on: The date time of the result submission
- compute_request: The foreign key of the compute request which spawned this result
- classification: The result of the classification against the model
- errors: A comma separated list of errors encountered during classification

It seems best, unless otherwise noted, that the result of a request be stored in a separate data table. Currently the only downside to this setup is that it doesn't provide a mechanism to mark requests as failed. A failed request could have improper datatypes, or have required too many system resources for the worker it was assigned to. In the future this may be something to consider.

### Dispatch_Token

```json
{
    "id": "primary key",
    "classification_id": "primary key of classification request",
    "dispatch_token": "generated token for the given request",
}
```

#### Description

The dispatch token model will be used as a layer of security in order to prevent malicious actors from submitting falsified results to the classification service. The dispatch tokens should be generated upon a worker instance's request for work.
