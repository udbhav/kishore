from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.shortcuts import render, redirect, get_object_or_404
from kishore.models import Cart, Product, CartItem, CartItemForm

class ProductIndex(ListView):
    queryset = Product.objects.filter(visible=True)
    context_object_name = "products"
    template_name = "kishore/store/product_list.html"

class ProductDetail(DetailView):
    queryset = Product.objects.filter(visible=True)
    context_object_name = "product"
    template_name = "kishore/store/product_detail.html"

def cart(request):
    cart = get_or_create_cart(request)
    return render(request, "kishore/store/cart.html", {'cart': cart})

def add_to_cart(request):
    if request.method == "POST":
        cart = get_or_create_cart(request)
        form = CartItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)

            # check to see we don't already have this product in the cart
            if cart.cartitem_set.filter(product=item.product).count() > 0:
                item_to_update = cart.cartitem_set.filter(product=item.product)[0]
                item_to_update.quantity = item_to_update.quantity + item.quantity
                item_to_update.save()
            else:
                item.unit_price = item.product.price
                item.cart = cart
                item.save()

        return redirect("kishore_cart")
    else:
        return HttpResponse("Bad request", status=400)

def update_cart(request, item_id):
    if request.method == "POST":
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id)

        if item not in cart.cartitem_set.all():
            return HttpResponse("Bad request", status=400)

        form = CartItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()

        return redirect("kishore_cart")
    else:
        return HttpResponse("Bad request", status=400)

def remove_from_cart(request, item_id):
    if request.method == "POST":
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id)

        if item not in cart.cartitem_set.all():
            return HttpResponse("Bad request", status=400)

        item.delete()
        return redirect("kishore_cart")
    else:
        return HttpResponse("Bad request", status=400)

def get_or_create_cart(request):
    cart, created = Cart.objects.get_or_create(pk=request.session.get('kishore_cart_id', None))

    if created:
        request.session['kishore_cart_id'] = cart.id

    return cart
