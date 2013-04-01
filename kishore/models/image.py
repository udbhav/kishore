from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill

class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='uploads/images')
    credit = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    position = models.IntegerField(default=1)
    medium_image = ImageSpecField(image_field='image', processors=[ResizeToFit(500,500),])
    thumbnail = ImageSpecField(image_field='image', processors=[ResizeToFill(60,60),])

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = 'kishore_images'
        app_label = 'kishore'
