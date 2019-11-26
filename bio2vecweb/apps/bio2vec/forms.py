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

VERSION_RE = re.compile('^(\d+\.)(\d+\.)(\d+)$')


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        exclude = (
            'created_by', 'date_created', 'modified_by', 'date_modified',
            'indexed',)
        help_texts = {
            'name': 'Name of the dataset',
            'description': 'Describe the dataset. What features are encoded?',
            'measurement_technique': 'What kind of method was used to generate embeddings?',
            'original_dataset': 'Link to the original dataset',
            'original_description': 'Provide small description of the original dataset',
            'evaluated_in': 'An Experiment in which the embeddings are evaluated. URL to OpenML.',
            'creators': '<url|orcid|text> separated by commas',
            'contributors': '<url|orcid|text> separated by commas',
            'publisher': '<url>',
            'keywords': 'Types of entities used in the dataset',
            'citation': 'A published reference for the publication'
        
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DatasetForm, self).__init__(*args, **kwargs)

        
    def save(self):
        if not self.instance.pk:
            self.instance = super(DatasetForm, self).save(commit=False)
            self.instance.created_by = self.request.user
        else:
            self.instance.modified_by = self.request.user
            self.instance.date_modified = timezone.now()
        self.instance.save()
        return self.instance

class DistributionForm(forms.ModelForm):

    class Meta:
        model = Distribution
        exclude = (
            'created_by', 'date_created', 'modified_by', 'date_modified',
            'embedding_size', 'dataset')
        help_texts = {
            'version': 'major.minor.patch',
        }
    
    embeddings_file = forms.FileField(
        validators=[validators.FileExtensionValidator(['tsv', 'gz']),],
        help_text='*.tsv or *.tsv.gz file with embeddings')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.dataset = kwargs.pop('dataset', None)
        super(DistributionForm, self).__init__(*args, **kwargs)

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
        self.instance.embedding_size = embedding_size
        return embeddings_file

    def clean_version(self):
        version = self.cleaned_data['version']
        if not VERSION_RE.match(version):
            raise forms.ValidationError('Version format should be MAJOR.MINOR.PATCH')
        return version
        
    def save(self):
        if not self.instance.pk:
            self.instance = super(DistributionForm, self).save(commit=False)
            self.instance.created_by = self.request.user
            self.instance.dataset = self.dataset
        else:
            self.instance.modified_by = self.request.user
            self.instance.date_modified = timezone.now()
        self.instance.save()
        if not self.instance.indexed:
            index_dataset.delay(self.dataset.pk)
        return self.instance
