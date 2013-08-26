from django.conf.urls import *
from django.contrib.auth import urls as auth_urls
from django.contrib.auth.decorators import login_required

from kishore.views import (OrderList, OrderDetail, ArtistAdminList, ArtistCreate, ArtistUpdate,
                           ArtistDelete, ImageList, ImageJSONList, ImageCreate, ImageUpdate,
                           ImageDelete)

import auth as auth_urls

urlpatterns = patterns(
    '',
    url(r'^$', 'kishore.views.admin_dashboard', name='kishore_admin_dashboard'),

    url(r'^orders/$', OrderList.as_view(), name='kishore_admin_orders'),
    url(r'^orders/(?P<pk>\d+)/$', OrderDetail.as_view(), name='kishore_admin_order_detail'),
    url(r'^orders/(?P<pk>\d+)/ship/$', 'kishore.views.ship_order',name='kishore_admin_ship_order'),
    url(r'^orders/(?P<pk>\d+)/refund/$', 'kishore.views.refund_order',
        name='kishore_admin_refund_order'),
    url(r'^orders/(?P<pk>\d+)/hide/$', 'kishore.views.hide_order', name='kishore_admin_hide_order'),

    url(r'^artists/$', ArtistAdminList.as_view(), name='kishore_admin_artists'),
    url(r'^artists/create/$', ArtistCreate.as_view(), name='kishore_admin_artist_create'),
    url(r'^artists/(?P<pk>\d+)/$', ArtistUpdate.as_view(), name='kishore_admin_artist_update'),
    url(r'^artists/(?P<pk>\d+)/delete/$', ArtistDelete.as_view(), name='kishore_admin_artist_delete'),

    url(r'^images/$', ImageList.as_view(), name='kishore_admin_images'),
    url(r'^images/json/$', ImageJSONList.as_view(),name='kishore_admin_images_json'),
    url(r'^images/create/$', ImageCreate.as_view(), name='kishore_admin_image_create'),
    url(r'^images/(?P<pk>\d+)/$', ImageUpdate.as_view(),name='kishore_admin_image_update'),
    url(r'^images/(?P<pk>\d+)/delete/$', ImageDelete.as_view(), name='kishore_admin_image_delete'),

    (r'^accounts/', include(auth_urls)),
)
