from django.conf.urls import *
from kishore.views import ArtistDetail, ArtistIndex, SongDetail, SongIndex, ReleaseDetail, ReleaseIndex

urlpatterns = patterns(
    '',
    url(r'^artists/$', ArtistIndex.as_view(), name='kishore_artists_index'),
    url(r'^artists/(?P<slug>[-\w]+)/$', ArtistDetail.as_view(), name='kishore_artist_detail'),

    url(r'^songs/$', SongIndex.as_view(), name='kishore_songs_index'),
    url(r'^songs/(?P<slug>[-\w]+)/$', SongDetail.as_view(), name='kishore_song_detail'),

    url(r'^releases/$', ReleaseIndex.as_view(), name='kishore_releases_index'),
    url(r'^releases/(?P<slug>[-\w]+)/$', ReleaseDetail.as_view(), name='kishore_release_detail'),
)
