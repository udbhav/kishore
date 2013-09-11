from django.conf.urls import *
from django.contrib.auth import urls as auth_urls
from django.contrib.auth.decorators import login_required
from kishore.views import (OrderList, OrderDetail, ArtistAdminList, ArtistCreate, ArtistUpdate,
                           ArtistDelete, ImageList, ImageJSONList, ImageCreate, ImageUpdate,
                           ImageDelete, SongAdminList, SongCreate, SongUpdate, SongDelete,
                           ReleaseAdminList, ReleaseCreate, ReleaseUpdate, ReleaseDelete,
                           UserList, UserCreate, UserUpdate, UserDelete, ProductAdminList,
                           ProductCreate, ProductUpdate, ProductDelete, SongJSONList, ProductSearch,
                           ArtistSearch, ReleaseSearch, SongSearch, OrderSearch, ImageSearch)

from kishore.models import ProductSearchForm

import auth as auth_urls

urlpatterns = patterns(
    '',
    url(r'^$', 'kishore.views.dashboard', name='kishore_admin_dashboard'),

    url(r'^orders/$', OrderList.as_view(), name='kishore_admin_orders'),
    url(r'^orders/search/$', OrderSearch.as_view(), name='kishore_admin_order_search'),
    url(r'^orders/(?P<pk>\d+)/$', OrderDetail.as_view(), name='kishore_admin_order_detail'),
    url(r'^orders/(?P<pk>\d+)/ship/$', 'kishore.views.ship_order',name='kishore_admin_ship_order'),
    url(r'^orders/(?P<pk>\d+)/refund/$', 'kishore.views.refund_order',
        name='kishore_admin_refund_order'),
    url(r'^orders/(?P<pk>\d+)/hide/$', 'kishore.views.hide_order', name='kishore_admin_hide_order'),

    url(r'^products/$', ProductAdminList.as_view(), name='kishore_admin_products'),
    url(r'^products/search/$', ProductSearch.as_view(), name='kishore_admin_product_search'),
    url(r'^products/create/$', ProductCreate.as_view(), name='kishore_admin_product_create'),
    url(r'^products/(?P<pk>\d+)/$', ProductUpdate.as_view(), name='kishore_admin_product_update'),
    url(r'^products/(?P<pk>\d+)/delete/$', ProductDelete.as_view(), name='kishore_admin_product_delete'),

    url(r'^artists/$', ArtistAdminList.as_view(), name='kishore_admin_artists'),
    url(r'^artists/search/$', ArtistSearch.as_view(), name='kishore_admin_artist_search'),
    url(r'^artists/create/$', ArtistCreate.as_view(), name='kishore_admin_artist_create'),
    url(r'^artists/(?P<pk>\d+)/$', ArtistUpdate.as_view(), name='kishore_admin_artist_update'),
    url(r'^artists/(?P<pk>\d+)/delete/$', ArtistDelete.as_view(), name='kishore_admin_artist_delete'),

    url(r'^songs/$', SongAdminList.as_view(), name='kishore_admin_songs'),
    url(r'^songs/search/$', SongSearch.as_view(), name='kishore_admin_song_search'),
    url(r'^songs/create/$', SongCreate.as_view(), name='kishore_admin_song_create'),
    url(r'^songs/(?P<pk>\d+)/$', SongUpdate.as_view(), name='kishore_admin_song_update'),
    url(r'^songs/(?P<pk>\d+)/delete/$', SongDelete.as_view(), name='kishore_admin_song_delete'),
    url(r'^songs/json/$', SongJSONList.as_view(),name='kishore_admin_songs_json'),

    url(r'^releases/$', ReleaseAdminList.as_view(), name='kishore_admin_releases'),
    url(r'^releases/search/$', ReleaseSearch.as_view(), name='kishore_admin_release_search'),
    url(r'^releases/create/$', ReleaseCreate.as_view(), name='kishore_admin_release_create'),
    url(r'^releases/(?P<pk>\d+)/$', ReleaseUpdate.as_view(), name='kishore_admin_release_update'),
    url(r'^releases/(?P<pk>\d+)/delete/$', ReleaseDelete.as_view(),
        name='kishore_admin_release_delete'),

    url(r'^users/$', UserList.as_view(), name='kishore_admin_users'),
    url(r'^users/create/$', UserCreate.as_view(), name='kishore_admin_user_create'),
    url(r'^users/(?P<pk>\d+)/$', UserUpdate.as_view(), name='kishore_admin_user_update'),
    url(r'^users/(?P<pk>\d+)/delete/$', UserDelete.as_view(), name='kishore_admin_user_delete'),

    url(r'^images/$', ImageList.as_view(), name='kishore_admin_images'),
    url(r'^images/search/$', ImageSearch.as_view(), name='kishore_admin_image_search'),
    url(r'^images/create/$', ImageCreate.as_view(), name='kishore_admin_image_create'),
    url(r'^images/(?P<pk>\d+)/$', ImageUpdate.as_view(),name='kishore_admin_image_update'),
    url(r'^images/(?P<pk>\d+)/delete/$', ImageDelete.as_view(), name='kishore_admin_image_delete'),
    url(r'^images/json/$', ImageJSONList.as_view(),name='kishore_admin_images_json'),

    (r'^accounts/', include(auth_urls)),
)
