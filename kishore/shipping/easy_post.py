from django import forms
from django.conf import settings
from django.shortcuts import render, redirect

import easypost
from easypost import Error as EasypostError

from kishore.templatetags.kishore_tags import kishore_currency
from kishore.models import Order, Address
from kishore import settings as kishore_settings
from kishore import utils

EASYPOST_SERVICES = {
    'Priority': 'USPS Priority Mail: 3-4 days',
    'Express': 'USPS Priority Mail Express: 1-2 days',
    'MediaMail': 'USPS Media Mail: 3-8 days',
    }

class ShippingMethodForm(forms.Form):
    method = forms.CharField()

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(ShippingMethodForm, self).__init__(*args, **kwargs)

        if request:
            shipment_id = request.session.get("kishore_shipment_id",None)
            shipment = easypost.Shipment.retrieve(id = shipment_id)
            self.fields['method'] = forms.ChoiceField(widget=forms.RadioSelect, choices=self.get_rate_choices(shipment['rates']))

    def get_rate_choices(self, rates):
        choices = []

        for r in rates:
            description = EASYPOST_SERVICES.get(r['service'], None)
            if description:
                choices.append([r['id'], "%s %s" % (kishore_currency(r['rate']), description)])

        return choices

class AddressForm(forms.Form):
    name = forms.CharField(widget=utils.KishoreTextInput())
    street_address = forms.CharField(widget=utils.KishoreTextInput())
    street_address2 = forms.CharField(required=False,
                                      widget=utils.KishoreTextInput(),
                                      label="Street Address 2")
    city = forms.CharField(widget=utils.KishoreTextInput())
    state = forms.CharField(widget=utils.KishoreTextInput())
    country = forms.CharField(initial="USA", widget=utils.KishoreTextInput())
    zipcode = forms.CharField(widget=utils.KishoreTextInput())

    def clean(self):
        cleaned_data = super(AddressForm, self).clean()

        try:
            address = easypost.Address.create(
                name = cleaned_data["name"],
                street1 = cleaned_data["street_address"],
                street2 = cleaned_data["street_address2"],
                city = cleaned_data["city"],
                state = cleaned_data["state"],
                zip = cleaned_data["zipcode"],
                country = cleaned_data["country"],
                )
        except Exception as e:
            raise forms.ValidationError(e)
        else:
            self.easypost_address = address.verify()
        return cleaned_data

class EasyPostBackend(object):
    shipping_method_form = ShippingMethodForm
    address_form = AddressForm
    easypost = easypost

    def __init__(self):
        self.set_api_key()

    def set_api_key(self):
        key = getattr(settings, "EASYPOST_API_KEY", None)

        if not key:
            raise Exception("You must set EASYPOST_API_KEY")

        easypost.api_key = key

    @property
    def from_address(self):
        address_id = getattr(settings, "EASYPOST_FROM_ADDRESS_ID", None)

        if not address_id:
            raise Exception("You must set EASYPOST_FROM_ADDRESSS_ID")

        return easypost.Address.retrieve(id = address_id)

    def shipping_view(self, request):
        if request.method == "POST":
            form = self.address_form(request.POST)

            if form.is_valid():
                to_address = form.easypost_address
                cart = utils.get_or_create_cart(request)

                parcel = easypost.Parcel.create(
                    length = 12,
                    width = 12,
                    height = 4,
                    weight = cart.total_weight,
                    )

                shipment = easypost.Shipment.create(
                    to_address = to_address,
                    from_address = self.from_address,
                    parcel = parcel,
                    )

                request.session['kishore_shipment_id'] = shipment["id"]

                return redirect("kishore_shipping_methods")
        else:
            form = self.address_form()

        return render(request, "kishore/store/easypost_shipping.html", {'form': form})

    def shipping_method_view(self, request):
        cart = utils.get_or_create_cart(request)

        if request.method == "POST":
            form = self.shipping_method_form(request.POST, request=request)

            if form.is_valid():
                shipment_id = request.session.get("kishore_shipment_id",None)
                shipment = easypost.Shipment.retrieve(id=shipment_id)
                rate_id = form.cleaned_data["method"]
                shipping_total = [r.rate for r in shipment.rates if r.id == rate_id][0]

                order = Order.objects.create(
                    shipment_processor = kishore_settings.KISHORE_SHIPPING_BACKEND,
                    shipment_id = shipment_id,
                    shipment_method_id = rate_id,
                    shipping_address = self.create_shipping_address(shipment.to_address),
                    shipping_total = shipping_total)

                request.session['kishore_order_id'] = order.id
                return redirect("kishore_payment")
        else:
            form = self.shipping_method_form(request=request)

        return render(request, "kishore/store/shipping_method.html",{'form':form})

    def ship_order_view(self, request, order):
        shipment = easypost.Shipment.retrieve(order.shipment_id)

        if request.method == "POST":
            if request.POST.get("buy_postage"):
                rate = [r for r in shipment.rates if r.id == order.shipment_method_id][0]
                shipment.buy(rate=rate)
            else:
                order.shipped = True
                order.save()
                return redirect("kishore_admin_dashboard")

        return render(request, "kishore/admin/easypost_ship_order.html", {'order':order,'shipment':shipment})

    def create_shipping_address(self, address):
        street2 = address.get("street2","")
        if not street2:
            street2 = ""

        address = Address.objects.create(
            name = address.get("name",""),
            street_address = address.get("street1",""),
            street_address2 = street2,
            city = address.get("city",""),
            state = address.get("state",""),
            zipcode = address.get("zip",""),
            country = address.get("country",""))

        return address
