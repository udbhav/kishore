from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

from music import Artist, Release, Song
from store import Product

class KishoreSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['searchqueryset'] = SearchQuerySet().models(Artist, Release, Song, Product)
        super(KishoreSearchForm, self).__init__(*args, **kwargs)
