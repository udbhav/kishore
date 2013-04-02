from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from kishore.models import Product, Cart, CartItem
from kishore.views import get_or_create_cart
from base import KishoreTestCase

class ProductTestCase(KishoreTestCase):
    def test_index(self):
        resp = self.client.get(reverse('kishore_products_index'))

    def test_detail(self):
        p = Product.objects.get(pk=1)
        resp = self.client.get(p.get_absolute_url())
        self.assertEqual(resp.status_code, 200)

class CartTestCase(KishoreTestCase):
    def test_cart_operations(self):
        # see if we can create a cart
        resp = self.client.get(reverse('kishore_cart'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.client.session['kishore_cart_id'])

        # try adding to a cart, should add successfully and redirect
        resp = self.client.post(reverse('kishore_add_to_cart'), {'product': 1, 'quantity': 5})
        self.assertEqual(resp.status_code, 302)

        # try updating cart item quantity
        resp = self.client.post(reverse('kishore_update_cart', kwargs={'item_id': 1}), {'quantity':2})
        self.assertEqual(resp.status_code, 302)

        # try updating a cart item that doesn't belong to our cart
        other_cart = Cart.objects.create()
        other_item = CartItem.objects.create(cart=other_cart, product=Product.objects.all()[0])
        resp = self.client.post(reverse('kishore_update_cart', kwargs={'item_id': other_item.id}), {'quantity':2})
        self.assertEqual(resp.status_code, 400)

        # try removing a cart item
        resp = self.client.post(reverse('kishore_remove_from_cart', kwargs={'item_id': 1}))
        self.assertEqual(resp.status_code, 302)

        # try removing an item that doesn't belong to us
        resp = self.client.post(reverse('kishore_remove_from_cart', kwargs={'item_id': other_item.id}))
        self.assertEqual(resp.status_code, 400)
