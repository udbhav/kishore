from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

from kishore import settings as kishore_settings
from music import Artist, Release, Song
from store import Product

class KishoreSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        models = [Release, Song, Product]

        if kishore_settings.KISHORE_LABEL_LAYOUT:
            models.append(Artist)

        kwargs['searchqueryset'] = SearchQuerySet().models(*models)
        super(KishoreSearchForm, self).__init__(*args, **kwargs)
