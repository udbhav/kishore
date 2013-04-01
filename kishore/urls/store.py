from django.conf.urls import *

urlpatterns = patterns(
    '',
    url(r'^add-to-cart/$', 'kishore.views.add_to_cart', name='kishore_add_to_cart'),
)
