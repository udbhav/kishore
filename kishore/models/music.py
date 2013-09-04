from datetime import datetime, date
import json

from django.db import models
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify

from kishore import settings as kishore_settings
from kishore import utils
from image import ModelFormWithImages
from players import DefaultPlayer

class WithSlug(models.Model):
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

        super(WithSlug, self).save(*args, **kwargs)

    def get_slug_origin(self):
        if hasattr(self,'name'):
            return getattr(self, 'name')
        elif hasattr(self, 'title'):
            return getattr(self, 'title')
        else:
            return self.pk

class Artist(WithSlug):
    name = models.CharField(max_length=120)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    images = models.ManyToManyField('Image', through='ArtistImage', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('kishore_artist_detail', kwargs={'slug':self.slug})

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
        db_table = 'kishore_artist_images'
        app_label = 'kishore'

class MusicBase(models.Model):
    artist = models.ForeignKey(Artist)
    title = models.CharField(max_length=100)
    release_date = models.DateField(default=date.today())
    description = models.TextField(blank=True)
    remote_url = models.CharField(max_length=100, blank=True, help_text="URL to external service hosting the audio, Soundcloud, etc")
    streamable = models.BooleanField(default=True)
    downloadable = models.BooleanField()

    def __unicode__(self):
        if kishore_settings.KISHORE_LABEL_LAYOUT:
            return '%s - %s' % (self.artist.name, self.title)
        else:
            return self.title

    def get_player(self):
        if not self.remote_url:
            return DefaultPlayer(self)
        else:
            for backend in kishore_settings.KISHORE_AUDIO_BACKENDS:
                player = utils.load_class(backend)(self)
                if player.accepts_remote_url(self.remote_url):
                    return player

    def get_player_html(self):
        if self.streamable:
            player = self.get_player()
            return player.get_player_html()
        else:
            return None

    def get_primary_image(self):
        images = self.ordered_images()
        if images:
            return images[0].image

    class Meta:
        abstract = True

class Song(WithSlug, MusicBase):
    audio_file = models.FileField(upload_to='uploads/music', blank=True, null=True,storage=utils.load_class(kishore_settings.KISHORE_STORAGE_BACKEND)())
    artwork = models.ManyToManyField('Image', through='SongImage', blank=True, null=True)

    def download_link(self):
        if self.audio_file and self.downloadable:
            return self.audio_file.url
        else:
            return None

    def get_absolute_url(self):
        return reverse('kishore_song_detail', kwargs={'slug': self.slug})

    def ordered_images(self):
        return SongImage.objects.filter(song=self).order_by('position')

    def images_as_json(self):
        return json.dumps([i.image.json_safe_values for i in self.ordered_images()])

    @property
    def json_safe_values(self):
        return {'pk': self.pk,
                'title':self.__unicode__(),
                }

    class Meta:
        db_table = 'kishore_songs'
        app_label = 'kishore'

class SongImage(models.Model):
    song = models.ForeignKey(Song)
    image = models.ForeignKey('Image')
    position = models.IntegerField(default=1)

    class Meta:
        db_table = 'kishore_song_images'
        app_label = 'kishore'

class Release(WithSlug, MusicBase):
    songs = models.ManyToManyField(Song, through='ReleaseSong', blank=True, null=True)
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
            form.fields["product"].widget = forms.RadioSelect()
            form.fields["product"].queryset = Product.objects.filter(id__in=ids)
            form.fields["product"].empty_label = None
            return form
        else:
            return None


    def get_absolute_url(self):
        return reverse('kishore_release_detail', kwargs={'slug': self.slug})

    def ordered_images(self):
        return ReleaseImage.objects.filter(release=self).order_by('position')

    def images_as_json(self):
        return json.dumps([i.image.json_safe_values for i in self.ordered_images()])

    class Meta:
        db_table = 'kishore_releases'
        app_label = 'kishore'

class ReleaseImage(models.Model):
    release = models.ForeignKey(Release)
    image = models.ForeignKey('Image')
    position = models.IntegerField(default=1)

    class Meta:
        db_table = 'kishore_release_images'
        app_label = 'kishore'

class ReleaseSong(models.Model):
    release = models.ForeignKey(Release)
    song = models.ForeignKey('Song')
    track_number = models.IntegerField(default=1)

    class Meta:
        db_table = 'kishore_release_songs'
        app_label = 'kishore'

class ArtistForm(ModelFormWithImages):
    artist_images = forms.CharField(widget=forms.HiddenInput(attrs={'class':'kishore-images-input'}))
    images_field_name = 'artist_images'
    object_id_name = 'artist_id'
    through_model = ArtistImage

    class Meta:
        model = Artist
        fields = ('name','url','description','artist_images','slug')
        widgets = {
            'name': utils.KishoreTextInput(),
            'slug': utils.KishoreTextInput(),
            'url': utils.KishoreTextInput(),
            'description': forms.Textarea(attrs={'class':'kishore-editor-input'})
        }

class SongForm(ModelFormWithImages):
    artist = forms.ModelChoiceField(queryset=Artist.objects.all(),
                                    empty_label=None,
                                    widget=utils.KishoreSelectWidget())
    song_images = forms.CharField(label="Artwork",
                                     widget=forms.HiddenInput(attrs={'class':'kishore-images-input'}))
    images_field_name = 'song_images'
    object_id_name = 'song_id'
    through_model = SongImage

    class Meta:
        model = Song
        fields = ('artist','title','remote_url','audio_file', 'release_date','streamable',
                  'downloadable','description','song_images','slug')

        widgets = {
            'title': utils.KishoreTextInput(),
            'slug': utils.KishoreTextInput(),
            'release_date': utils.KishoreTextInput(),
            'remote_url': utils.KishoreTextInput(),
            'description': forms.Textarea(attrs={'class':'kishore-editor-input'})
            }

class ReleaseForm(ModelFormWithImages):
    artist = forms.ModelChoiceField(queryset=Artist.objects.all(),
                                    empty_label=None,
                                    widget=utils.KishoreSelectWidget())
    release_images = forms.CharField(label="Artwork",
                                     widget=forms.HiddenInput(attrs={'class':'kishore-images-input'}))
    images_field_name = 'release_images'
    object_id_name = 'release_id'
    through_model = ReleaseImage

    class Meta:
        model = Release
        fields = ('artist','title','remote_url', 'release_date','streamable',
                  'downloadable','description','release_images','slug')

        widgets = {
            'title': utils.KishoreTextInput(),
            'slug': utils.KishoreTextInput(),
            'release_date': utils.KishoreTextInput(),
            'remote_url': utils.KishoreTextInput(),
            'description': forms.Textarea(attrs={'class':'kishore-editor-input'})
            }
