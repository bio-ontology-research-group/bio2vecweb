from django import forms
from django.utils import timezone
from django.db.models import Max
import json
from bio2vec.models import Dataset, Distribution
import shutil
import os
import re
import gzip
from django.conf import settings
from django.core import validators
from django.core.files.uploadedfile import TemporaryUploadedFile

from bio2vec.tasks import index_dataset

EMBEDDING_FILE_HEADER = (
    'IRI', 'Label', 'Alternative IRIs',
    'Synonyms', 'Entity Type', 'Embedding Vector'
)


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        exclude = (
            'created_by', 'date_created', 'modified_by', 'date_modified',
            'indexed',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DatasetForm, self).__init__(*args, **kwargs)


class DistributionForm(forms.ModelForm):

    class Meta:
        model = Distribution
        exclude = (
            'created_by', 'date_created', 'modified_by', 'date_modified',
            'embedding_size',)
    
    embeddings_file = forms.FileField(
        validators=[validators.FileExtensionValidator(['tsv', 'gz']),])

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DatasetForm, self).__init__(*args, **kwargs)

    def validate_line(self, line):
        it = line.strip().split('\t')
        if len(it) != 6:
            raise forms.ValidationError(
                'TSV file should have five columns (%s, %s, %s, %s, %s, %s)' % (
                    EMBEDDING_FILE_HEADER))
        embed = it[5].split(',')
        if len(embed) < 2:
            raise forms.ValidationError(
                'Embedding vector length should be greater than 2')
        try:
            embed = list(map(float, embed))
        except ValueError as e:
            raise forms.ValidationError(
                'Embedding vector elements should be real numbers')
        return len(embed)

    def clean_embeddings_file(self):
        """Check embeddings tab-separated file format
        """
        embeddings_file = self.cleaned_data['embeddings_file']
        if not isinstance(embeddings_file, TemporaryUploadedFile):
            return embeddings_file
        
        file_path = embeddings_file.temporary_file_path()
        _, ext = os.path.splitext(file_path)
        if ext == '.gz':
            try:
                itr = gzip.open(file_path, 'rt')
            except Exception as e:
                print(e)
                raise forms.ValidationError('Invalid file format')
        else:
            itr = open(file_path, 'rt')
        line = next(itr)
        embedding_size = self.validate_line(line)
        c = 0
        # Validate first 10 lines of the file
        for line in itr:
            embed_size = self.validate_line(line)
            if embed_size != embedding_size:
                raise forms.ValidationError('All embeddings should have same size')
            c += 1
            if c == 10:
                break
        self.instance.indexed = False
        return embeddings_file
        
    def save(self):
        if not self.instance.pk:
            self.instance = super(DistributionForm, self).save(commit=False)
            self.instance.created_by = self.request.user
        else:
            self.instance.modified_by = self.request.user
            self.instance.date_modified = timezone.now()
        self.instance.save()
        if not self.instance.indexed:
            index_dataset.delay(self.instance.pk)
        return self.instance
