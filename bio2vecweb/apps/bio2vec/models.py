from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone

def dataset_directory_path(instance, filename):
    return 'id{0:06d}/{1}'.format(instance.created_by.pk, filename)

class Dataset(models.Model):

    name = models.CharField(max_length=127, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_datasets')
    date_created = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='modified_datasets')
    date_modified = models.DateTimeField(blank=True, null=True)
    entity_types = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    creators = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    contributors = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    source_link = models.CharField(max_length=255, blank=True, null=True)
    original_dataset = models.CharField(max_length=255, blank=True, null=True)
    publications = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    experiment = models.CharField(max_length=127, blank=True, null=True)
    model = models.CharField(max_length=127, blank=True, null=True)
    embeddings_file = models.FileField(upload_to=dataset_directory_path)
    indexed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Datasets'

    def __str__(self):
        return self.name

    @property
    def index_name(self):
        return 'dataset_' + str(self.pk)


class Entity(models.Model):
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE,
        related_name='entities')
    iri = models.CharField(max_length=127, db_index=True)
    alternative_iris = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    entity_type = models.CharField(max_length=127)
    label = models.CharField(max_length=127)
    description = models.TextField(blank=True, null=True)
    vector = ArrayField(models.FloatField())
    pca_x = models.FloatField(default=0.0)
    pca_y = models.FloatField(default=0.0)

    class Meta:
        verbose_name_plural = 'Entities'
        unique_together = ('dataset', 'iri')

    def __str__(self):
        return self.iri
