import json

from django.views.generic import DetailView, ListView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from taggit.models import Tag

from kishore.models import Artist, Song, Release, Product, CartItemForm, KishorePaginator

class ArtistList(ListView):
    model = Artist
    context_object_name = "artists"
    template_name = "kishore/music/artist_list.html"

class ArtistDetail(DetailView):
    queryset = Artist.objects.all()
    context_object_name = "artist"
    template_name = "kishore/music/artist_detail.html"

class ArtistsByTag(ListView):
    model = Artist
    context_object_name = "artists"
    template_name = "kishore/music/artist_list.html"

    def get_queryset(self):
        return Artist.objects.filter(tags__slug__in=[self.kwargs['tag']])

    def get_context_data(self, **kwargs):
        context = super(ArtistsByTag, self).get_context_data(**kwargs)
        tag = get_object_or_404(Tag, slug=self.kwargs['tag'])
        context['title'] = "Artists tagged %s" % tag.name
        return context

class ArtistSongList(ListView):
    model = Song
    template_name = "kishore/music/artist_songs.html"
    context_object_name = "songs"
    paginate_by = 25
    paginator_class = KishorePaginator

    def get_artist(self):
        self.artist = get_object_or_404(Artist, slug=self.kwargs['slug'])
        return self.artist

    def get_queryset(self):
        artist = self.get_artist()
        return Song.objects.filter(artist=artist)

    def get_context_data(self, **kwargs):
        context = super(ArtistSongList, self).get_context_data(**kwargs)
        context["artist"] = self.artist
        return context

class SongList(ListView):
    model = Song
    context_object_name = "songs"
    template_name = "kishore/music/song_list.html"
    paginate_by = 25
    paginator_class = KishorePaginator

class SongsByTag(ListView):
    model = Song
    context_object_name = "songs"
    template_name = "kishore/music/song_list.html"
    paginate_by = 25
    paginator_class = KishorePaginator

    def get_queryset(self):
        return Song.objects.filter(tags__slug__in=[self.kwargs['tag']])

    def get_context_data(self, **kwargs):
        context = super(SongsByTag, self).get_context_data(**kwargs)
        tag = get_object_or_404(Tag, slug=self.kwargs['tag'])
        context['title'] = "Songs tagged %s" % tag.name
        return context

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

class ReleasesByTag(ListView):
    model = Release
    context_object_name = "releases"
    template_name = "kishore/music/release_list.html"
    paginate_by = 25
    paginator_class = KishorePaginator

    def get_queryset(self):
        return Release.objects.filter(tags__slug__in=[self.kwargs['tag']])

    def get_context_data(self, **kwargs):
        context = super(ReleasesByTag, self).get_context_data(**kwargs)
        tag = get_object_or_404(Tag, slug=self.kwargs['tag'])
        context['title'] = "Releases tagged %s" % tag.name
        return context

def play_song(request):
    if request.is_ajax() and request.method == 'POST':
        song_ids = json.loads(request.POST.get('song_ids', None))
        songs = Song.objects.filter(id__in=song_ids)
        song_urls = {}
        for song in songs:
            song_urls[song.id] = song.audio_file.url

        data = json.dumps(song_urls)
        mimetype = 'application/json'
        return HttpResponse(data,mimetype)
    else:
        return HttpResponse("Bad request", status=400)
