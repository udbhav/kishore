from django.db import models
from taggit.managers import TaggableManager

class TaggableModel(models.Model):
    tags = TaggableManager(blank=True)

    class Meta:
        abstract = True
