from django.db import models
from django.utils import timezone
from datetime import datetime

class CachedModel(models.Model):
    last_modified = models.DateTimeField(auto_now_add=True)

    @property
    def cache_key(self):
        return 'kishore/%s/%s-%s' %  (self.__class__.__name__,
                                      self.id,
                                      self.last_modified)

    def save(self, *args, **kwargs):
        self.last_modified = timezone.now()

        if hasattr(self, 'get_cached_siblings'):
            siblings = self.get_cached_siblings()

            for x in siblings:
                if x:
                    x.last_modified = timezone.now()
                    x.save()

        super(CachedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
