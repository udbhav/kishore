from django.db import models
from django import forms
from django.core.urlresolvers import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill

from kishore.utils import KishoreTextInput

class Image(models.Model):
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='uploads/images')
    credit = models.CharField(max_length=100, blank=True)
    credit_url = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    medium_image = ImageSpecField(image_field='image', processors=[ResizeToFit(500,500),])
    thumbnail = ImageSpecField(image_field='image', processors=[ResizeToFill(60,60),])
    cropped_square = ImageSpecField(image_field='image', processors=[ResizeToFill(300,300),])

    def __unicode__(self):
        return self.title

    @property
    def json_safe_values(self):
        return {'pk': self.pk,
                'image_url':self.cropped_square.url,
                'admin_url':self.get_admin_url(),
                'title':self.title,
                }

    def get_admin_url(self):
        return reverse("kishore_admin_image_update", kwargs={'pk':self.pk})

    class Meta:
        db_table = 'kishore_images'
        app_label = 'kishore'




class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        widgets = {
            'title': KishoreTextInput(),
            'credit': KishoreTextInput(),
            'credit_url': KishoreTextInput(),
        }
