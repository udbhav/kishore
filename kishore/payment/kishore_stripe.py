from django.shortcuts import render
from django import forms
from django.conf import settings
import stripe

from kishore import settings as kishore_settings

class StripeForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput)

class StripeBackend(object):
    human_name = "Credit Card"
    valid = True

    def __init__(self, order):
        self.order = order

    def get_response(self, request):
        form = StripeForm()
        key = self.get_api_key(secret=False)
        return render(request, "kishore/store/stripe.html",{'form':form,'key':key,'order':self.order})

    def accept_payment(self, request):

        token = request.POST["token"]
        stripe.api_key = self.get_api_key()

        if self.order.total == 0:
            return False

        try:
            charge = stripe.Charge.create(
                amount=int(self.order.total*100),
                currency=kishore_settings.KISHORE_CURRENCY,
                card=token,
                description=self.order.id
                )
        except stripe.CardError, e:
            return False
        else:
            self.order.transaction_id = charge.id
            self.order.save()
            return True

    def refund_order(self):
        stripe.api_key = self.get_api_key()
        charge = stripe.Charge.retrieve(self.order.transaction_id)
        charge.refund()

    def get_api_key(self, secret=True):
        if secret:
            var = "KISHORE_STRIPE_SECRET_KEY"
        else:
            var = "KISHORE_STRIPE_PUBLISHABLE_KEY"

        key = getattr(settings, var, None)
        if key:
            return key
        else:
            raise Exception("You must set %s" % var)
