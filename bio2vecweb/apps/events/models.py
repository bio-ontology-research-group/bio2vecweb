from django.db import models
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='events')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_date = models.DateTimeField(default=timezone.now)
    
