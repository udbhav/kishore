from django.forms import TextInput

def load_class(name):
    name = str(name)
    mod = __import__(name.rsplit(".",1)[0], fromlist=[name.rsplit(".",1)[1]])
    return getattr(mod, name.rsplit(".",1)[1])

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



class KishoreTextInput(TextInput):
    def __init__(self, attrs=None):
        if not attrs:
            attrs = {'class':'form-control'}
        else:
            if not attrs.get('class'):
                attrs['class'] = 'form-control'

        super(KishoreTextInput, self).__init__(attrs)
