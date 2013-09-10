import json

from django import forms
from django.http import HttpResponse
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, Page

def load_class(name):
    name = str(name)
    mod = __import__(name.rsplit(".",1)[0], fromlist=[name.rsplit(".",1)[1]])
    return getattr(mod, name.rsplit(".",1)[1])

def get_cart(request):
    from kishore.models import Cart

    cart_id = request.session.get('kishore_cart_id', None)
    if cart_id:
        try:
            return Cart.objects.get(pk=cart_id)
        except Cart.DoesNotExist:
            request.session['kishore_cart_id'] = None
            return None

def get_or_create_cart(request):
    from kishore.models import Cart

    cart, created = Cart.objects.get_or_create(pk=request.session.get('kishore_cart_id', None))

    if created:
        request.session['kishore_cart_id'] = cart.id

    return cart

def get_or_create_order(request):
    from kishore.models import Order

    order, created = Order.objects.get_or_create(pk=request.session.get('kishore_order_id', None))

    if created:
        request.session['kishore_order_id'] = order.id

    return order

def clear_session_vars(request):
    request.session["kishore_cart_id"] = None
    request.session["kishore_order_id"] = None



class KishoreWidget(object):
    def __init__(self, attrs=None):
        if not attrs:
            attrs = {'class':'form-control'}
        else:
            if not attrs.get('class'):
                attrs['class'] = 'form-control'

        super(KishoreWidget, self).__init__(attrs)

class KishoreTextInput(KishoreWidget, forms.TextInput):
    pass

class KishoreSelectWidget(KishoreWidget, forms.Select):
    pass

class KishorePasswordInput(KishoreWidget, forms.PasswordInput):
    pass

class JSONResponseMixin(object):
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        json_context = {}
        for key, value in context.items():
            try:
                json.dumps(value)
            except TypeError:
                if value.__class__ == QuerySet:
                    json_context[key] = [getattr(x, 'json_safe_values', None) for x in value]
                elif value.__class__ == Page:
                    json_context['page'] = {'page':value.number,
                                            'has_next': value.has_next(),
                                            'has_previous': value.has_previous(),
                                            }
            else:
                json_context[key] = value

        return json.dumps(json_context)
