from urllib import urlencode
from urlparse import parse_qs

from django.shortcuts import render
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
import requests

from kishore import settings as kishore_settings
from base import BaseBackend

class PaypalDigitalBackend(BaseBackend):
    human_name = 'Paypal'

    @property
    def valid(self):
        return not self.order.shippable

    def get_response(self, request):
        # site = Site.objects.get_current()
        # root = "http://%s" % site.domain

        # paypal_dict = {
        #     "cmd": "_xclick",
        #     "business": settings.KISHORE_PAYPAL_EMAIL,
        #     "amount": str(self.order.total),
        #     "item_name": "Order #: %s" % self.order.id,
        #     "return": "%s%s" % (root, reverse('kishore_process_payment')),
        #     "cancel_return": root,
        #     "item_number": self.order.id,
        #     "no_shipping": 1,
        #     "shipping": 0,
        # }

        # url = kishore_settings.KISHORE_PAYPAL_SUBMIT_URL + "?" + urlencode(paypal_dict)
        # return url

        return render(request, "kishore/store/paypal_digital.html")

    def accept_payment(self, request):
        self.order.transaction

    def make_request(self, method, params=None):
        credentials = self.get_credentials()
        request_params = (
            ('METHOD', method),
            ('USER', credentials['username']),
            ('PWD', credentials['password']),
            ('SIGNATURE', credentials['signature']),
            ('VERSION', 89),
        )

        if params:
            request_params += params

        r = requests.post(kishore_settings.KISHORE_PAYPAL_CLASSIC_ENDPOINT,
                          data=urlencode(request_params))
        return r

    def test_request(self):
        site = Site.objects.get_current()
        root = "http://%s" % site.domain
        name = 'Order #%s' % self.order.id
        total = str(self.order.total)

        params = (
            ('NOSHIPPING', 1),
            ('EMAIL', self.order.customer_email),
            ('PAYMENTREQUEST_0_AMT', total),
            ('PAYMENTREQUEST_0_PAYMENTACTION', 'SALE'),
            ('PAYMENTREQUEST_0_CURRENCYCODE', kishore_settings.KISHORE_CURRENCY.upper()),
            ('PAYMENTREQUEST_0_AMT', total),
            ('PAYMENTREQUEST_0_DESC', name),
            ('PAYMENTREQUEST_0_INVNUM', self.order.id),
            ('cancelUrl', root),
            ('returnUrl', "%s%s" % (root, reverse('kishore_process_payment'))),

            ('L_PAYMENTREQUEST_0_NAME0', name),
            ('L_PAYMENTREQUEST_0_AMT0', total),
            ('L_PAYMENTREQUEST_0_QTY0', 1),
            ('L_PAYMENTREQUEST_0_ITEMCATEGORY0', 'Digital'),
        )

        r = self.make_request('SetExpressCheckout', params)

        if r.ok:
            response = parse_qs(r.text)
            if response['ACK'][0] == 'Success':
                url = "%s%s%s" % (kishore_settings.KISHORE_PAYPAL_SUBMIT_URL,
                                  "?cmd=_express-checkout&token=",
                                  response['TOKEN'][0])
                return url

        return r

    def set_express_checkout(self):
        site = Site.objects.get_current()
        root = "http://%s" % site.domain

        params = (
            ('cancelUrl', root),
            ('returnUrl', "%s%s" % (root, reverse('kishore_process_payment'))),
            ('PAYMENTREQUEST_0_CURRENCYCODE', kishore_settings.KISHORE_CURRENCY.upper()),
            ('PAYMENTREQUEST_0_AMT', str(self.order.total)),
            ('PAYMENTREQUEST_0_PAYMENTACTION', 'SALE'),
            ('PAYMENTREQUEST_0_ITEMAMT', str(self.order.total)),
            ('L_PAYMENTREQUEST_0_ITEMCATEGORY0', 'Digital'),
            ('L_PAYMENTREQUEST_0_NAME0', 'Order #%s' % self.order.id),
            ('L_PAYMENTREQUEST_0_QTY',1),
            ('L_PAYMENTREQUEST_0_AMT0', str(self.order.total)),
        )

        return self.make_request('SetExpressCheckout', params)

    def get_credentials(self):
        username = getattr(settings, 'KISHORE_PAYPAL_CLASSIC_USERNAME', None)
        password = getattr(settings, 'KISHORE_PAYPAL_CLASSIC_PASSWORD', None)
        signature = getattr(settings, 'KISHORE_PAYPAL_CLASSIC_SIGNATURE', None)
        email = getattr(settings, 'KISHORE_PAYPAL_EMAIL', None)

        if not username or not password or not signature or not email:
            raise Exception("Please set KISHORE_PAYPAL_CLASSIC_USERNAME "
                            "KISHORE_PAYPAL_CLASSIC_PASSWORD, KISHORE_PAYPAL_EMAIL, and "
                            "KISHORE_PAYPAL_CLASSIC_SIGNATURE")

        return {'username': username, 'password': password, 'signature': signature, 'email': email}


def test():
    from kishore.models import Order
    o = Order.objects.get(pk=9)
    p = PaypalDigitalBackend(o)
    return p.test_request()
