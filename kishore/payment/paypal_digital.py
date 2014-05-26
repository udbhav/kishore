from urllib import urlencode
from urlparse import parse_qs
import logging

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
import requests

from kishore import settings as kishore_settings
from base import BaseBackend

logger = logging.getLogger('kishore')

class PaypalDigitalBackend(BaseBackend):
    human_name = 'Paypal'

    @property
    def valid(self):
        return not self.order.shippable

    def get_response(self, request):
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
                return redirect(url)
        else:
            logger.error("problem with paypal digital: %s" % r.text)
            return render(request, "kishore/store/paypal_digital.html",
                          {'error': True})

    def accept_payment(self, request):
        token = request.GET.get("token", None)
        payer_id = request.GET.get("PayerID", None)

        if token and payer_id:
            params = (
                ('TOKEN', token),
                ('PAYMENTACTION', 'Sale'),
                ('PAYERID', payer_id),
                ('PAYMENTREQUEST_0_AMT', self.order.total),
            )
            r = self.make_request('DoExpressCheckoutPayment', params)
            if r.ok:
                response = parse_qs(r.text)
                if response['ACK'][0] == 'Success':
                    self.order.transaction_id = response['PAYMENTINFO_0_TRANSACTIONID'][0]
                    self.order.save()
                    return True

        return False

    def refund_order(self):
        r = self.make_request('RefundTransaction', (
            ('TRANSACTIONID', self.order.transaction_id),
        ))
        r.raise_for_status()
        response = parse_qs(r.text)

        if response['ACK'][0] == 'Success':
            return True
        else:
            raise Exception("Problem with refund")

    def make_request(self, method, params=None):
        username = getattr(settings, 'KISHORE_PAYPAL_CLASSIC_USERNAME', None)
        password = getattr(settings, 'KISHORE_PAYPAL_CLASSIC_PASSWORD', None)
        signature = getattr(settings, 'KISHORE_PAYPAL_CLASSIC_SIGNATURE', None)
        email = getattr(settings, 'KISHORE_PAYPAL_EMAIL', None)

        if not username or not password or not signature or not email:
            raise Exception("Please set KISHORE_PAYPAL_CLASSIC_USERNAME "
                            "KISHORE_PAYPAL_CLASSIC_PASSWORD, "
                            "KISHORE_PAYPAL_EMAIL, and "
                            "KISHORE_PAYPAL_CLASSIC_SIGNATURE")

        request_params = (
            ('METHOD', method),
            ('USER', username),
            ('PWD', password),
            ('SIGNATURE', signature),
            ('VERSION', kishore_settings.KISHORE_PAYPAL_CLASSIC_VERSION),
        )

        if params:
            request_params += params

        r = requests.post(kishore_settings.KISHORE_PAYPAL_CLASSIC_ENDPOINT,
                          data=urlencode(request_params))
        return r

def test():
    from kishore.models import Order
    o = Order.objects.get(pk=9)
    p = PaypalDigitalBackend(o)
    return p.accept_payment('x')
