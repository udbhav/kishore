from django.conf.urls import *
from haystack.views import SearchView

from kishore.models import KishoreSearchForm

urlpatterns = patterns(
    '',
    url(r'^$', SearchView(form_class=KishoreSearchForm), name='kishore_search'),
    )
