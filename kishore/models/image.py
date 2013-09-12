import json

from django.db import models
from django import forms
from django.core.urlresolvers import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill

from kishore import utils
from tags import TaggableModel

class Image(TaggableModel):
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='uploads/images')
    credit = models.CharField(max_length=100, blank=True)
    credit_url = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    medium_image = ImageSpecField(source='image', processors=[ResizeToFit(500,500),])
    thumbnail = ImageSpecField(source='image', processors=[ResizeToFill(100,100),])
    cropped_square = ImageSpecField(source='image', processors=[ResizeToFill(500,500),])

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
            'title': utils.KishoreTextInput(),
            'credit': utils.KishoreTextInput(),
            'credit_url': utils.KishoreTextInput(),
            'tags': utils.KishoreTagWidget(),
            'description': forms.Textarea(attrs={'class':'kishore-editor-input'})
        }

class ModelFormWithImages(forms.ModelForm):
    images_field_name = 'images'
    through_model = models.Model

    def __init__(self, *args, **kwargs):
        super(ModelFormWithImages, self).__init__(*args, **kwargs)

        if not self.is_bound:
            self.initial[self.images_field_name] = self.instance.images_as_json

    def save(self):
        super(ModelFormWithImages, self).save()

        images = json.loads(self.cleaned_data[self.images_field_name])
        for i, image in enumerate(images):
            object_image, created = self.through_model.objects.get_or_create(
                **{'image_id': image['pk'],
                   self.object_id_name: self.instance.id,
                   }
                  )
            if object_image.position != i:
                object_image.position = i
                object_image.save()

        object_images = self.through_model.objects.filter(**{
                self.object_id_name:self.instance.id})

        for object_image in object_images:
            matches = [x for x in images if x['pk'] == object_image.image_id]
            if len(matches) == 0:
                object_image.delete()
