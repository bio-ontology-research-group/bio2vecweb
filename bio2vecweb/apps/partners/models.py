from django.db import models


class ResearchGroup(models.Model):

    name = models.CharField(max_length=127, unique=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
    

class Member(models.Model):
    group = models.ForeignKey(
        ResearchGroup, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=127)
    position = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='members')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
