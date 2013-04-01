from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from kishore.models import Cart, Product

class ProductIndex(ListView):
    queryset = Product.objects.filter(visible=True)
    context_object_name = "products"
    template_name = "kishore/store/product_list.html"

class ProductDetail(DetailView):
    queryset = Product.objects.filter(visible=True)
    context_object_name = "product"
    template_name = "kishore/store/product_detail.html"

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
