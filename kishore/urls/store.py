from django.conf.urls import *
from kishore.views import (ProductDetail, ProductList, ProductsByTag, add_to_cart, cart, update_cart,
                           remove_from_cart, checkout, shipping, shipping_methods, payment,
                           process_payment, download, process_download, BuyNow)

urlpatterns = patterns(
    '',
    url(r'^$', ProductList.as_view(), name='kishore_store'),

    url(r'^products/(?P<slug>[-\w]+)/$', ProductDetail.as_view(), name='kishore_product_detail'),
    url(r'^products/(?P<slug>[-\w]+)/buy/$', BuyNow.as_view(), name='kishore_buy_now'),
    url(r'^products/tagged/(?P<tag>[-\w]+)/$', ProductsByTag.as_view(),
        name='kishore_products_by_tag'),

    url(r'^cart/$', cart, name='kishore_cart'),
    url(r'^cart/add/$', add_to_cart, name='kishore_add_to_cart'),
    url(r'^cart/update/(?P<item_id>\d+)/$', update_cart, name='kishore_update_cart'),
    url(r'^cart/remove/(?P<item_id>\d+)/$', remove_from_cart, name='kishore_remove_from_cart'),

    url(r'^checkout/$', checkout, name='kishore_checkout'),
    url(r'^shipping/$', shipping, name='kishore_shipping'),
    url(r'^shipping/methods/$', shipping_methods, name='kishore_shipping_methods'),
    url(r'^payment/$', payment, name='kishore_payment'),
    url(r'^payment/process/$', process_payment, name='kishore_process_payment'),

    url(r'^download/(?P<download_key>\w+)/$', download, name='kishore_download'),
    url(r'^download/process/(?P<download_key>\w+)/(?P<product_id>\d+)/$', process_download, name='kishore_process_download'),
)
