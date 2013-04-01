from datetime import datetime

from django.db import models
from django.core.urlresolvers import reverse
from music import Song, Release
from image import Image

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    inventory = models.IntegerField(default=-1)
    images = models.ManyToManyField(Image, blank=True, null=True)
    visible = models.BooleanField(default=True)

    def __unicode__(self):
        if self.subclass:
            return self.subclass.__unicode__()
        else:
            return self.name

    @property
    def subclass(self):
        subclasses = ('digitalsong', 'digitalrelease', 'physicalrelease', 'merch')
        for s in subclasses:
            if hasattr(self, s):
                return getattr(self, s)
        return None

    def get_absolute_url(self):
        return reverse('kishore_product_detail',kwargs={'slug':self.slug})

    def formatted_price(self):
        return "%01.2f" % self.price

    class Meta:
        db_table = 'kishore_products'
        app_label = 'kishore'

class DigitalSong(Product):
    song = models.OneToOneField(Song)

    class Meta:
        db_table = 'kishore_digitalsongs'
        app_label = 'kishore'

class DigitalRelease(Product):
    release = models.ForeignKey(Release)
    zipfile = models.FileField(upload_to='uploads/store')

    def __unicode__(self):
        return "%s - %s" % (self.release, self.name)

    class Meta:
        db_table = 'kishore_digitalreleases'
        app_label = 'kishore'

class PhysicalRelease(Product):
    release = models.ForeignKey(Release)

    def __unicode__(self):
        return "%s - %s" % (self.release, self.name)

    class Meta:
        db_table = 'kishore_physicalreleases'
        app_label = 'kishore'

class MerchVariant(models.Model):
    name = models.CharField(max_length=100)
    price_difference = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField(default=0)
    images = models.ManyToManyField(Image)

    class Meta:
        db_table = 'kishore_merchvariants'
        app_label = 'kishore'

class Merch(Product):
    variants = models.ManyToManyField(MerchVariant)

    class Meta:
        db_table = 'kishore_merch'
        app_label = 'kishore'
