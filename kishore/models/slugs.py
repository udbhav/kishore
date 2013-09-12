from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist

class SlugModel(models.Model):
    slug = models.SlugField(unique=True,blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            valid_slug = False
            i = 0
            while not valid_slug:
                if i == 0:
                    proposed_slug = slugify(self.get_slug_origin())
                else:
                    proposed_slug = slugify("%s %s" % (self.get_slug_origin(), i))
                try:
                    self.__class__.objects.get(slug=proposed_slug)
                except ObjectDoesNotExist:
                    valid_slug = True
                else:
                    i += 1

            self.slug = proposed_slug

        super(SlugModel, self).save(*args, **kwargs)

    def get_slug_origin(self):
        if hasattr(self,'name'):
            return getattr(self, 'name')
        elif hasattr(self, 'title'):
            return getattr(self, 'title')
        else:
            return self.pk
