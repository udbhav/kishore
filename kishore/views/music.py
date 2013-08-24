from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404
from kishore.models import Artist, Song, Release, Product, CartItemForm

class ArtistList(ListView):
    model = Artist
    context_object_name = "artists"
    template_name = "kishore/music/artist_list.html"

class ArtistDetail(ListView):
    model = Release
    context_object_name = "releases"
    template_name = "kishore/music/release_list.html"

    def get_artist(self):
        self.artist = get_object_or_404(Artist, slug=self.kwargs['slug'])
        return self.artist

    def get_queryset(self):
        artist = self.get_artist()
        return Release.objects.filter(artist=artist)

    def get_context_data(self, **kwargs):
        # call base implementation
        context = super(ArtistDetail, self).get_context_data(**kwargs)
        context["artist"] = self.get_artist()
        return context

class SongList(ListView):
    model = Song
    context_object_name = "songs"
    template_name = "kishore/music/song_list.html"

class SongDetail(DetailView):
    queryset = Song.objects.all()
    context_object_name = "song"
    template_name = "kishore/music/song_detail.html"

class ReleaseList(ListView):
    model = Release
    context_object_name = "releases"
    template_name = "kishore/music/release_list.html"

class ReleaseDetail(DetailView):
    queryset = Release.objects.all()
    context_object_name = "release"
    template_name = "kishore/music/release_detail.html"
