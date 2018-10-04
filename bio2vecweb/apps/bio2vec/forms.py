from django import forms
from django.utils import timezone
from django.db.models import Max
import json
from bio2vec.models import Dataset
import shutil
import os
from django.conf import settings
from django.core import validators


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        exclude = (
            'created_by', 'date_created', 'modified_by', 'date_modified',
            'indexed',)

    embeddings_file = forms.FileField(
        validators=[validators.FileExtensionValidator(['json',]),])
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DatasetForm, self).__init__(*args, **kwargs)

    def clean_embeddings_file(self):
        embeddings_file = self.cleaned_data['embeddings_file']
        for line in embeddings_file:
            print(line)
        return embeddings_file
        
    def save(self):
        if not self.instance.pk:
            self.instance = super(DatasetForm, self).save(commit=False)
            self.instance.created_by = self.request.user
        else:
            self.instance.modified_by = self.request.user
            self.instance.date_modified = timezone.now()
        self.instance.save()
        return self.instance
