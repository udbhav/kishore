import json

import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.shortcuts import redirect

from kishore import settings as kishore_settings

class PaypalBackend(object):
    human_name = 'Paypal'

    def __init__(self, order):
        self.order = order

    @property
    def valid(self):
        return self.order.shippable

    def get_response(self, request):
        url = kishore_settings.KISHORE_PAYPAL_ENDPOINT + '/payments/payment'
        data = json.dumps({
            'intent': 'sale',
            'redirect_urls': {
                'return_url': "http://%s%s" % (Site.objects.get_current(),
                                        reverse('kishore_process_payment')),
                'cancel_url': "http://%s" % Site.objects.get_current(),
                },
            'payer': {'payment_method':'paypal'},
            'transactions': [{
                    'amount': {
                            'total': str(self.order.total),
                            'currency': kishore_settings.KISHORE_CURRENCY.upper(),
                            },
                    'description': "Order #: %s" % self.order.id,
                    }]
            })

        r = requests.post(url,data=data,headers={
                'Content-Type':'application/json',
                'Authorization':"Bearer %s" % self.get_access_token(),
                })

        if r.ok and r.json()['state'] == 'created':
            data = r.json()
            self.order.transaction_id = data["id"]
            self.order.save()

            link = [l["href"] for l in data["links"] if l["rel"] == "approval_url"][0]
            return redirect(link)
        else:
            r.raise_for_status()
            raise Exception('Problem with creating payment for Paypal')

    def accept_payment(self, request):
        url = "%s/payments/payment/%s/execute" % (settings.KISHORE_PAYPAL_ENDPOINT,
                                                  self.order.transaction_id)
        data = json.dumps({'payer_id': request.GET["PayerID"]})
        r = requests.post(url,data=data,headers={
                'Content-Type': 'application/json',
                'Authorization': "Bearer %s" % self.get_access_token(),
                })

        r.raise_for_status()

        self.order.transaction_id = r.json()['transactions'][0]['related_resources'][0]['sale']['id']
        self.order.save()
        return True

    def refund_order(self):
        url = "%s/payments/sale/%s/refund" % (settings.KISHORE_PAYPAL_ENDPOINT,
                                              self.order.transaction_id)
        r = requests.post(url,data='{}',headers={
                'Content-Type': 'application/json',
                'Authorization': "Bearer %s" % self.get_access_token(),
                })

        r.raise_for_status()
        return r

    def get_access_token(self):
        client_id, secret = self.get_credentials()
        url = kishore_settings.KISHORE_PAYPAL_ENDPOINT + '/oauth2/token'
        r = requests.post(url,
                          auth=requests.auth.HTTPBasicAuth(client_id, secret),
                          params={'grant_type': 'client_credentials'},
                          headers={'Content-Type':'application/x-www-form-urlencoded'})

        if r.ok:
            return r.json()['access_token']
        else:
            r.raise_for_status()

    def get_credentials(self):
        client_id = getattr(settings, 'KISHORE_PAYPAL_CLIENT_ID', None)
        secret = getattr(settings, 'KISHORE_PAYPAL_SECRET', None)

        if not client_id or not secret:
            raise Exception('Please set KISHORE_PAYPAL_CLIENT_ID and KISHORE_PAYPAL_SECRET')

        else:
            return client_id, secret
