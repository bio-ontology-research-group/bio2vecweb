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
    original_dataset = models.CharField(max_length=255, blank=True, null=True)
    original_description = models.TextField(blank=True, null=True)
    creators = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    contributors = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    keywords = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    citation = models.CharField(max_length=127, blank=True, null=True)
    measurement_technique = models.CharField(max_length=127, blank=True, null=True)
    evaluated_in = models.CharField(max_length=127, blank=True, null=True)
    indexed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Datasets'

    def __str__(self):
        return self.name

    @property
    def index_name(self):
        return 'dataset_' + str(self.pk)

    def get_latest_dist(self):
        return self.distributions.order_by('-pk').first()


class Distribution(models.Model):
    CC0 = 'CC0'
    CCBY = 'CC BY'
    CCBYNC = 'CC BY-NC'
    LICENSES = [
        (CC0, CC0),
        (CCBY, CCBY),
        (CCBYNC, CCBYNC),
    ]
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='distributions')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_distributions')
    date_created = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='modified_distributions')
    date_modified = models.DateTimeField(blank=True, null=True)
    version = models.CharField(max_length=31)
    embeddings_file = models.FileField(upload_to=dataset_directory_path)
    embedding_size = models.PositiveIntegerField()
    license = models.CharField(max_length=31, choices=LICENSES, default=CC0)
    
    class Meta:
        verbose_name_plural = 'Distributions'

    def __str__(self):
        return self.dataset.name + ' ' + self.version

    
class Entity(models.Model):
    distribution = models.ForeignKey(
        Distribution, on_delete=models.CASCADE,
        related_name='entities')
    entity_type = models.CharField(max_length=127)
    iri = models.CharField(max_length=127, db_index=True)
    alternative_iris = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    name = models.CharField(max_length=127)
    synonyms = ArrayField(
        models.CharField(max_length=127), blank=True, null=True)
    embedding = ArrayField(models.FloatField())
    pca_x = models.FloatField(default=0.0)
    pca_y = models.FloatField(default=0.0)

    class Meta:
        verbose_name_plural = 'Entities'
        unique_together = ('distribution', 'iri')

    def __str__(self):
        return self.iri
