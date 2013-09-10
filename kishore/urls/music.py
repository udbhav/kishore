from django.conf.urls import *
from kishore.views import ArtistDetail, ArtistList, SongDetail, SongList, ReleaseDetail, ReleaseList

urlpatterns = patterns(
    '',
    url(r'^artists/$', ArtistList.as_view(), name='kishore_artists_index'),
    url(r'^artists/(?P<slug>[-\w]+)/$', ArtistDetail.as_view(), name='kishore_artist_detail'),

    url(r'^songs/$', SongList.as_view(), name='kishore_songs_index'),
    url(r'^songs/play/$', 'kishore.views.play_song', {}, 'kishore_song_play'),
    url(r'^songs/(?P<slug>[-\w]+)/$', SongDetail.as_view(), name='kishore_song_detail'),

    url(r'^releases/$', ReleaseList.as_view(), name='kishore_releases_index'),
    url(r'^releases/(?P<slug>[-\w]+)/$', ReleaseDetail.as_view(), name='kishore_release_detail'),
)
