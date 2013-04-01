from datetime import datetime

from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from kishore import settings as kishore_settings

class Artist(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('kishore_artist_detail', kwargs={'slug':self.slug})

    class Meta:
        db_table = 'kishore_artists'
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
    artwork = models.ManyToManyField('Image', blank=True, null=True)

    def __unicode__(self):
        if kishore_settings.KISHORE_LAYOUT == "label":
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
    audio_file = models.FileField(upload_to='uploads/music', blank=True, null=True)
    track_number = models.IntegerField(null=True, blank=True)

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

class Release(MusicBase):
    songs = models.ManyToManyField(Song, blank=True, null=True)

    def get_product_ids(self):
        count = self.physicalrelease_set.count() + self.digitalrelease_set.count()
        if count > 0:
            products = []
            products.extend([x.product_ptr_id for x in self.physicalrelease_set.all()])
            products.extend([x.product_ptr_id for x in self.digitalrelease_set.all()])
            return products
        else:
            return None

    def get_absolute_url(self):
        return reverse('kishore_release_detail', kwargs={'slug': self.slug})

    class Meta:
        db_table = 'kishore_releases'
        app_label = 'kishore'
