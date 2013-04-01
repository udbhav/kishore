from django.http import HttpResponse
from kishore.models import Cart

def add_to_cart(request):
    if request.method == "POST":
        cart = get_or_create_cart(request)

    else:
        return HttpResponse("Bad request", status=400)

def get_or_create_cart(request):
    cart, created = Cart.objects.get_or_create(id=request.session.get('kishore_cart_id', None))

    if created:
        request.session['kishore_cart_id'] = cart.id

    return cart
