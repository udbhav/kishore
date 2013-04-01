from django.core.urlresolvers import reverse

from kishore.models import Artist, Song, Release
from base import KishoreTestCase

class ArtistTestCase(KishoreTestCase):
    def test_index(self):
        resp = self.client.get(reverse('kishore_artists_index'))
        self.assertEqual(resp.status_code, 200)

    def test_detail(self):
        a = Artist.objects.get(pk=1)
        resp = self.client.get(a.get_absolute_url())
        self.assertEqual(resp.status_code, 200)

class SongTestCase(KishoreTestCase):
    def test_index(self):
        resp = self.client.get(reverse('kishore_songs_index'))
        self.assertEqual(resp.status_code, 200)

    def test_detail(self):
        s = Song.objects.get(pk=1)
        resp = self.client.get(s.get_absolute_url())
        self.assertEqual(resp.status_code, 200)

    def test_player_html(self):
        with self.settings(KISHORE_AUDIO_PLAYER="kishore.models.SoundcloudPlayer"):
            s = Song.objects.get(pk=1)
            self.assertTrue(s.get_player_html())

            # try non-streamable song
            s = Song.objects.get(pk=2)
            self.assertFalse(s.get_player_html())

    def test_download_link(self):
        s = Song.objects.get(pk=1)
        self.assertTrue(s.download_link())

        # try non-downloadable song
        s = Song.objects.get(pk=2)
        self.assertFalse(s.download_link())

class ReleaseTestCase(KishoreTestCase):
    def test_index(self):
        resp = self.client.get(reverse('kishore_releases_index'))
        self.assertEqual(resp.status_code, 200)

    def test_detail(self):
        r = Release.objects.get(pk=1)
        resp = self.client.get(r.get_absolute_url())
        self.assertEqual(resp.status_code, 200)

    def test_player_html(self):
        with self.settings(KISHORE_AUDIO_PLAYER="kishore.models.SoundcloudPlayer"):
            r = Release.objects.get(pk=1)
            self.assertTrue(r.get_player_html())

            # try non-streamable
            r = Release.objects.get(pk=2)
            self.assertFalse(r.get_player_html())
