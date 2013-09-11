from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

from kishore import settings as kishore_settings
from music import Artist, Release, Song
from store import Product, Order
from image import Image

class KishoreSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        models = [Release, Song, Product]

        if kishore_settings.KISHORE_LABEL_LAYOUT:
            models.append(Artist)

        kwargs['searchqueryset'] = SearchQuerySet().models(*models)
        super(KishoreSearchForm, self).__init__(*args, **kwargs)

class ProductSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['searchqueryset'] = SearchQuerySet().models(Product)
        super(ProductSearchForm, self).__init__(*args, **kwargs)

class ArtistSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['searchqueryset'] = SearchQuerySet().models(Artist)
        super(ArtistSearchForm, self).__init__(*args, **kwargs)

class SongSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['searchqueryset'] = SearchQuerySet().models(Song)
        super(SongSearchForm, self).__init__(*args, **kwargs)

class ReleaseSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['searchqueryset'] = SearchQuerySet().models(Release)
        super(ReleaseSearchForm, self).__init__(*args, **kwargs)

class ImageSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['searchqueryset'] = SearchQuerySet().models(Image)
        super(ImageSearchForm, self).__init__(*args, **kwargs)

class OrderSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        kwargs['searchqueryset'] = SearchQuerySet().models(Order)
        super(OrderSearchForm, self).__init__(*args, **kwargs)
