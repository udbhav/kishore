from datetime import datetime
import json

from django.db import models
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify

from kishore import settings as kishore_settings
from kishore import utils

class Artist(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True,blank=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    images = models.ManyToManyField('Image', through='ArtistImage', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('kishore_artist_detail', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super(Artist, self).save(*args, **kwargs)

    def ordered_images(self):
        return ArtistImage.objects.filter(artist=self).order_by('position')

    def images_as_json(self):
        return json.dumps([i.image.json_safe_values for i in self.ordered_images()])

    class Meta:
        db_table = 'kishore_artists'
        app_label = 'kishore'

class ArtistImage(models.Model):
    artist = models.ForeignKey(Artist)
    image = models.ForeignKey('Image')
    position = models.IntegerField(default=1)

    class Meta:
        db_table = 'kishore_artist_galleries'
        app_label = 'kishore'

class MusicBase(models.Model):
    artist = models.ForeignKey(Artist)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    date = models.DateTimeField(default=datetime.now())
    description = models.TextField(blank=True)
    remote_url = models.CharField(max_length=100, blank=True, help_text="URL to external service hosting the audio, Soundcloud, etc")
    streamable = models.BooleanField()
    downloadable = models.BooleanField()

    def __unicode__(self):
        if kishore_settings.KISHORE_LABEL_LAYOUT:
            return '%s - %s' % (self.artist.name, self.title)
        else:
            return self.title

    def get_player_backend(self):
        try:
            player_class_string = kishore_settings.KISHORE_AUDIO_PLAYER.rsplit(".", 1)
            mod = __import__(player_class_string[0], fromlist=[player_class_string[1]])
            klass = getattr(mod, player_class_string[1])
        except (ImportError, AttributeError):
            raise ImproperlyConfigured("Something is wrong with your KISHORE_AUDIO_PLAYER setting")
        return klass

    def get_player_html(self):
        if self.streamable:
            backend_klass = self.get_player_backend()
            player = backend_klass(self)
            return player.get_player_html()
        else:
            return None

    class Meta:
        abstract = True

class Song(MusicBase):
    audio_file = models.FileField(upload_to='uploads/music', blank=True, null=True,storage=utils.load_class(kishore_settings.KISHORE_STORAGE_BACKEND)())
    track_number = models.IntegerField(null=True, blank=True)
    artwork = models.ManyToManyField('Image', through='SongImage', blank=True, null=True)

    def download_link(self):
        if self.audio_file and self.downloadable:
            return self.audio_file.url
        else:
            return None

    def get_absolute_url(self):
        return reverse('kishore_song_detail', kwargs={'slug': self.slug})

    class Meta:
        db_table = 'kishore_songs'
        app_label = 'kishore'

class SongImage(models.Model):
    song = models.ForeignKey(Song)
    image = models.ForeignKey('Image')
    position = models.IntegerField(default=1)

    class Meta:
        db_table = 'kishore_song_galleries'
        app_label = 'kishore'

class Release(MusicBase):
    songs = models.ManyToManyField(Song, blank=True, null=True)
    artwork = models.ManyToManyField('Image', through='ReleaseImage', blank=True, null=True)

    def get_product_ids(self):
        count = self.physicalrelease_set.count() + self.digitalrelease_set.count()
        if count > 0:
            products = []
            products.extend([x.product_ptr_id for x in self.physicalrelease_set.all()])
            products.extend([x.product_ptr_id for x in self.digitalrelease_set.all()])
            return products
        else:
            return None

    def get_cart_form(self):
        from products import CartItemForm, Product
        ids = self.get_product_ids()
        if ids:
            form = CartItemForm()
            form.fields["product"].widget = forms.Select()
            form.fields["product"].queryset = Product.objects.filter(id__in=ids)
            form.fields["product"].empty_label = None
            return form
        else:
            return None


    def get_absolute_url(self):
        return reverse('kishore_release_detail', kwargs={'slug': self.slug})

    class Meta:
        db_table = 'kishore_releases'
        app_label = 'kishore'

class ReleaseImage(models.Model):
    release = models.ForeignKey(Release)
    image = models.ForeignKey('Image')
    position = models.IntegerField(default=1)

    class Meta:
        db_table = 'kishore_release_galleries'
        app_label = 'kishore'

class ArtistForm(forms.ModelForm):
    artist_images = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ArtistForm, self).__init__(*args, **kwargs)

        if not self.is_bound:
            self.initial['artist_images'] = self.instance.images_as_json

    def save(self):
        super(ArtistForm, self).save()

        images = json.loads(self.cleaned_data['artist_images'])
        for i, image in enumerate(images):
            try:
                artist_image = ArtistImage.objects.get(image_id=image['pk'],artist=self.instance)
            except ObjectDoesNotExist:
                artist_image = ArtistImage(image_id=image['pk'],artist=self.instance)

            artist_image.position = i
            artist_image.save()

        for artist_image in self.instance.artistimage_set.all():
            matches = [x for x in images if x['pk'] == artist_image.image_id]
            if len(matches) == 0:
                artist_image.delete()

    class Meta:
        model = Artist
        exclude = ('images',)
        widgets = {
            'name': utils.KishoreTextInput(),
            'slug': utils.KishoreTextInput(),
            'url': utils.KishoreTextInput(),
        }
