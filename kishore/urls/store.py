from django.conf.urls import *
from kishore.views import ProductDetail, ProductIndex, add_to_cart, cart, update_cart, remove_from_cart

urlpatterns = patterns(
    '',
    url(r'^$', ProductIndex.as_view(), name='kishore_products_index'),
    url(r'^products/(?P<slug>[-\w]+)/$', ProductDetail.as_view(), name='kishore_product_detail'),
    url(r'^cart/$', cart, name='kishore_cart'),
    url(r'^cart/update/(?P<item_id>\d+)/$', update_cart, name='kishore_update_cart'),
    url(r'^cart/remove/(?P<item_id>\d+)/$', remove_from_cart, name='kishore_remove_from_cart'),
    url(r'^add-to-cart/$', add_to_cart, name='kishore_add_to_cart'),
)
