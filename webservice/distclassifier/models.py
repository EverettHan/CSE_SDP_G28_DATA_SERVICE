from datetime import datetime
from django.db import models
import json

class User(models.Model):
    """
    Currently a place holder. Acts as an owner for the dataset models
    """
    username = models.CharField(max_length=32)
    created_on = models.DateTimeField(auto_now=True)

    def is_valid(dictionary):
        return  ("username" in dictionary) and \
                ("created_on" in dictionary)


class Dataset(models.Model):
    """
    The dataset model. There should only be one of these created for each dataset.
    """
    name = models.CharField(max_length=128, blank=False)
    display_name = models.CharField(max_length=128, blank=False)
    description = models.TextField()
    img_width = models.IntegerField()
    img_height = models.IntegerField()
    maintain_ratio = models.BooleanField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def from_post(dictionary):
        if not Dataset.is_valid(dictionary):
            return None
        return Dataset(name=dictionary["name"], \
                       display_name=dictionary["display_name"], \
                       description=dictionary["description"], \
                       img_width=dictionary["img_width"], \
                       img_height=dictionary["img_height"], \
                       maintain_ratio=dictionary["maintain_ratio"], \
                       owner=1)

    # I'm not actually sure if any of these methods are necessary in the slightest
    def is_valid(dictionary):
        """
        Use this method to check the form submission fields.
        """
        return  ("name" in dictionary) and \
                ("display_name" in dictionary) and \
                ("description" in dictionary) and \
                ("img_width" in dictionary) and \
                ("img_height" in dictionary) and \
                ("maintain_ratio" in dictionary) and \
                ("owner" in dictionary)


class Model(models.Model):
    """
    This is the model entry. Each of these entries will be reference the Dataset for which they have been trained. They will also reference a file. The file referencing functionality is still to be determined.
    """
    name = models.CharField(max_length=128, blank=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    uploaded_on = models.DateTimeField(auto_now_add=True)  # time when saved for first time
    data = models.FileField(upload_to='files/%Y/%m/%d')

    def is_valid(dictionary):
        return  ("name" in dictionary) and \
                ("dataset" in dictionary) and \
                ("uploaded_on" in dictionary) and \
                ("data" in dictionary)


class ClassificationRequest(models.Model):
    """
    A request created by a user submission.
    """
    fulfilled = models.BooleanField(default=False)
    requested_on = models.DateTimeField()
    assigned_on = models.DateTimeField(default="1970-01-01T00:00:00.000000")
    # model = models.ForeignKey(Model, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='Covid Image')

    def is_valid(dictionary):
        return  ("fulfilled" in dictionary) and \
                ("requested_on" in dictionary) and \
                ("assigned_on" in dictionary) and \
                ("image" in dictionary)

    def to_json(self):
        d = dict()
        d['fulfilled'] = self.fulfilled
        d['requested_on'] = str(self.requested_on)
        d['assigned_on'] = str(self.assigned_on)
        d['image'] = self.image.name
        return json.dumps(d)


class ClassificationResult(models.Model):
    """
    The result of a classification request.
    """
    completed_on = models.DateTimeField(auto_now=True)
    compute_request = models.ForeignKey(ClassificationRequest, on_delete=models.CASCADE)
    classification = models.CharField(max_length=128)
    errors = models.TextField(default="")

    def is_valid(dictionary):
        return  ("completed_on" in dictionary) and \
                ("compute_request" in dictionary) and \
                ("classification" in dictionary)

    def to_json(self):
        d = dict()
        d['completed_on'] = str(self.completed_on)
        d['compute_request'] = self.compute_request.to_json()
        d['classification'] = self.classification
        d['errors'] = self.errors
        return json.dumps(d)


class ImageUpload(models.Model):
    image = models.ImageField('Uploaded Image', blank=False)
