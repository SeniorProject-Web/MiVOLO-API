from django import forms
from django.forms import ClearableFileInput
from .models import predictImageServiceModel

class ImageForm(forms.ModelForm):
    class Meta:
        model = predictImageServiceModel
        fields = ['image']
        widgets = {
            'image': ClearableFileInput(attrs={'multiple': True}),
        }