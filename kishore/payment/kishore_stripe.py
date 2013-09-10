from django.shortcuts import render
from django import forms
from django.conf import settings
import stripe

from kishore import settings as kishore_settings

class StripeForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput)

class StripeBackend(object):
    human_name = "Credit Card"

    def get_response(self, request, order):
        form = StripeForm()
        key = self.get_api_key(secret=False)
        return render(request, "kishore/store/stripe.html",{'form':form,'key':key,'order':order})

    def accept_payment(self, request, order):

        token = request.POST["token"]
        stripe.api_key = self.get_api_key()

        if order.total == 0:
            return False

        try:
            charge = stripe.Charge.create(
                amount=int(order.total*100),
                currency=kishore_settings.KISHORE_CURRENCY,
                card=token,
                description=order.id
                )
        except stripe.CardError, e:
            return False
        else:
            order.transaction_id = charge.id
            order.save()
            return True

    def refund_order(self, order):
        stripe.api_key = self.get_api_key()
        charge = stripe.Charge.retrieve(order.transaction_id)
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
