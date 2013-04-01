from django.core.urlresolvers import reverse

from kishore.models import Product
from base import KishoreTestCase

class ProductTestCase(KishoreTestCase):
    def test_index(self):
        resp = self.client.get(reverse('kishore_products_index'))

    def test_detail(self):
        p = Product.objects.get(pk=1)
        resp = self.client.get(p.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
