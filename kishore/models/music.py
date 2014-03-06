from datetime import datetime, date
import json

from django.db import models
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from kishore import settings as kishore_settings
from kishore import utils
from image import ModelFormWithImages
from players import DefaultPlayer
from cache import CachedModel
from slugs import SlugModel
from tags import TaggableModel

class Artist(SlugModel, CachedModel, TaggableModel):
    name = models.CharField(max_length=120)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    images = models.ManyToManyField('Image', through='ArtistImage', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('kishore_artist_detail', kwargs={'slug':self.slug})

    def get_admin_url(self):
        return reverse('kishore_admin_artist_update', kwargs={'pk':self.id})

    def ordered_images(self):
        return ArtistImage.objects.filter(artist=self).order_by('position')

    def get_primary_image(self):
        images = self.ordered_images()
        if images:
            return images[0].image

    def images_as_json(self):
        return json.dumps([i.image.json_safe_values for i in self.ordered_images()])

    def get_cached_siblings(self):
        releases = list(self.release_set.all())
        songs = list(self.song_set.all())
        return releases + songs

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

class MusicBase(TaggableModel):
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
        ordering = ['-release_date']

class Song(SlugModel, MusicBase, CachedModel):
    audio_file = models.FileField(upload_to='uploads/music', blank=True, null=True,storage=utils.load_class(kishore_settings.KISHORE_STORAGE_BACKEND)())
    artwork = models.ManyToManyField('Image', through='SongImage', blank=True, null=True)

    def download_link(self):
        if self.audio_file and self.downloadable:
            return self.audio_file.storage.download_url(self.audio_file.name)
        else:
            return None

    def get_absolute_url(self):
        return reverse('kishore_song_detail', kwargs={'slug': self.slug})

    def get_admin_url(self):
        return reverse('kishore_admin_song_update', kwargs={'pk':self.id})

    def ordered_images(self):
        return SongImage.objects.filter(song=self).order_by('position')

    def images_as_json(self):
        return json.dumps([i.image.json_safe_values for i in self.ordered_images()])

    @property
    def json_safe_values(self):
        return {'pk': self.pk,
                'title':self.__unicode__(),
                }

    def get_cart_form(self):
        from store import CartItemForm, Product

        ids = [x.id for x in self.digitalsong_set.filter(visible=True)]
        if ids:
            form = CartItemForm()
            form.fields["product"].widget = forms.RadioSelect()
            form.fields["product"].queryset = Product.objects.filter(id__in=ids)
            form.fields["product"].empty_label = None
            form.fields["quantity"].widget = forms.HiddenInput()
            return form
        else:
            return None

    def get_buy_now_link(self):
        try:
            product = self.digitalsong_set.all()[0]
        except KeyError:
            return ""
        else:
            return reverse("kishore_buy_now", kwargs={'slug': product.slug})

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

class Release(SlugModel, MusicBase, CachedModel):
    songs = models.ManyToManyField(Song, through='ReleaseSong', blank=True, null=True)
    artwork = models.ManyToManyField('Image', through='ReleaseImage', blank=True, null=True)

    def get_product_ids(self):
        count = self.physicalrelease_set.count() + self.digitalrelease_set.count()
        if count > 0:
            products = []

            # we want to make sure we don't get any out of stock products
            physical_releases = self.physicalrelease_set.filter(visible=True).exclude(
                Q(track_inventory=True) & Q(inventory__lte=0))

            products.extend([x.product_ptr_id for x in physical_releases])
            products.extend([x.product_ptr_id for x in self.digitalrelease_set.filter(visible=True)])
            return products
        else:
            return None

    def get_cart_form(self):
        from products import CartItemForm, Product
        ids = self.get_product_ids()
        if ids:
            form = CartItemForm()
            form.fields["product"].widget = forms.RadioSelect()
            form.fields["product"].queryset = Product.objects.filter(id__in=ids).filter(visible=True)
            form.fields["product"].empty_label = None
            form.fields["quantity"].widget = forms.HiddenInput()
            return form
        else:
            return None

    def get_absolute_url(self):
        return reverse('kishore_release_detail', kwargs={'slug': self.slug})

    def get_admin_url(self):
        return reverse('kishore_admin_release_update', kwargs={'pk':self.id})

    def ordered_images(self):
        return ReleaseImage.objects.filter(release=self).order_by('position')

    def ordered_songs(self):
        release_songs = ReleaseSong.objects.filter(release=self).order_by('track_number')
        return [r.song for r in release_songs if r.song.streamable]

    def songs_as_json(self):
        return json.dumps([s.json_safe_values for s in self.ordered_songs()])

    def images_as_json(self):
        return json.dumps([i.image.json_safe_values for i in self.ordered_images()])

    def get_downloads(self):
        if self.downloadable:
            return self.digitalrelease_set.all()

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
        fields = ('name','url','description','artist_images','tags','slug')
        widgets = {
            'name': utils.KishoreTextInput(),
            'slug': utils.KishoreTextInput(),
            'url': utils.KishoreTextInput(),
            'tags': utils.KishoreTagWidget(),
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
                  'downloadable','description','song_images','tags','slug')

        widgets = {
            'title': utils.KishoreTextInput(),
            'slug': utils.KishoreTextInput(),
            'release_date': utils.KishoreTextInput(),
            'remote_url': utils.KishoreTextInput(),
            'tags': utils.KishoreTagWidget(),
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
    release_songs = forms.CharField(label="Songs",
                                    widget=forms.HiddenInput(attrs={'class':'kishore-songs-input'}))
    through_model = ReleaseImage

    def __init__(self, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)

        if not self.is_bound:
            self.initial['release_songs'] = self.instance.songs_as_json

    def save(self):
        super(ReleaseForm, self).save()

        songs = json.loads(self.cleaned_data['release_songs'])
        for i, song in enumerate(songs):
            release_song, created = ReleaseSong.objects.get_or_create(
                song_id= song['pk'],
                release_id = self.instance.id
                )

            if release_song.track_number != i:
                release_song.track_number = i
                release_song.save()

        release_songs = ReleaseSong.objects.filter(release_id=self.instance.id)

        for release_song in release_songs:
            matches = [x for x in songs if x['pk'] == release_song.song_id]
            if len(matches) == 0:
                release_song.delete()

    class Meta:
        model = Release
        fields = ('artist','title','remote_url', 'release_date','streamable',
                  'downloadable','description','release_songs','release_images','tags','slug')

        widgets = {
            'title': utils.KishoreTextInput(),
            'slug': utils.KishoreTextInput(),
            'release_date': utils.KishoreTextInput(),
            'remote_url': utils.KishoreTextInput(),
            'tags': utils.KishoreTagWidget(),
            'description': forms.Textarea(attrs={'class':'kishore-editor-input'})
            }
