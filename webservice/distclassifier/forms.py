from django import forms
from .models import *


class ModelForm(forms.ModelForm):
    class Meta:
        model = Model
        fields = ['name', 'dataset', 'data']


class ClassificationRequestForm(forms.ModelForm):
    class Meta:
        model = ClassificationRequest
        fields = ['model', 'image']

class ClassifyForm(forms.Form):
    image = forms.FileField()
