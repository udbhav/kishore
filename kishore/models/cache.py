from django.db import models
from datetime import datetime

class CachedModel(models.Model):
    last_modified = models.DateTimeField(default=datetime.now())

    @property
    def cache_key(self):
        return 'kishore/%s/%s-%s' %  (self.__class__.__name__,
                                      self.id,
                                      self.last_modified)

    def save(self, *args, **kwargs):
        self.last_modified = datetime.now()

        if hasattr(self, 'get_cached_siblings'):
            siblings = self.get_cached_siblings()

            for x in siblings:
                x.last_modified = datetime.now()
                x.save()

        super(CachedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
