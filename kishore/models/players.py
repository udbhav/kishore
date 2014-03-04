from django.conf import settings
from django.template.loader import render_to_string
from requests.exceptions import HTTPError
import soundcloud

from kishore import settings as kishore_settings

class BasePlayer(object):
    def __init__(self, music_data):
        self.music_data = music_data

class SoundcloudPlayer(BasePlayer):
    def get_soundcloud_client(self):
        try:
            client_id = settings.SOUNDCLOUD_CLIENT_ID
        except AttributeError:
            raise ImproperlyConfigured("Please set SOUNDCLOUD_CLIENT_ID in settings.py")

        return soundcloud.Client(client_id=client_id)

    def get_player_html(self):
        client = self.get_soundcloud_client()

        if kishore_settings.KISHORE_USE_SOUNDCLOUD_EMBED:
            r = client.get("/oembed", url=self.music_data.remote_url)
            if r.status_code == 200:
                return r.html
            else:
                return ""
        else:
            r = client.get("/resolve", url=self.music_data.remote_url)
            if r.status_code == 200:
                url = "%s?client_id=%s" % (r.obj['stream_url'], settings.SOUNDCLOUD_CLIENT_ID)
                songs = [{'stream_url': url, 'title': self.music_data.__unicode__}]
                return render_to_string("kishore/music/kishore_player.html", {'songs':songs})
            else:
                return ""

    def accepts_remote_url(self, url):
        try:
            url.index("soundcloud.com")
        except ValueError:
            return False
        else:
            return True

class DefaultPlayer(BasePlayer):
    def get_player_html(self):
        if self.music_data.__class__.__name__ == 'Release':
            songs = self.music_data.ordered_songs
        else:
            songs = [self.music_data]

        return render_to_string("kishore/music/kishore_player.html", {'songs':songs})
