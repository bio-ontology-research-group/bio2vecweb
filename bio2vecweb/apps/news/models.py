from django.db import models
from django.utils import timezone

class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='news')
    news_date = models.DateTimeField()
    created_date = models.DateTimeField(default=timezone.now)
    
