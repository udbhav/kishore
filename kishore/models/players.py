from django.conf import settings
from requests.exceptions import HTTPError

import soundcloud

class SoundcloudPlayer(object):
    def __init__(self, music_data):
        self.music_data = music_data

    def get_soundcloud_client(self):
        try:
            client_id = settings.SOUNDCLOUD_CLIENT_ID
        except AttributeError:
            raise ImproperlyConfigured("Please set SOUNDCLOUD_CLIENT_ID in settings.py")

        return soundcloud.Client(client_id=client_id)

    def get_player_html(self):
        client = self.get_soundcloud_client()

        try:
            r = client.get("/oembed", url=self.music_data.remote_url)
        except HTTPError:
            return ""

        if r.status_code == 200:
            return r.html
        else:
            return ""
