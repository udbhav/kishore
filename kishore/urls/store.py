from django.conf.urls import *
from kishore.views import ProductDetail, ProductIndex, add_to_cart

urlpatterns = patterns(
    '',
    url(r'^$', ProductIndex.as_view(), name='kishore_products_index'),
    url(r'^products/(?P<slug>[-\w]+)/$', ProductDetail.as_view(), name='kishore_product_detail'),
    url(r'^add-to-cart/$', add_to_cart, name='kishore_add_to_cart'),
)
