from datetime import datetime, timedelta
import re
import json

from django.http import HttpResponse
from django.views.generic import DetailView, ListView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.urlresolvers import reverse
from taggit.models import Tag

from kishore.models import Cart, Product, CartItem, CartItemForm, Order, PaymentForm, DownloadLink, DigitalRelease, KishorePaginator
from kishore import settings as kishore_settings
from kishore import utils

class ProductList(ListView):
    queryset = Product.objects.filter(visible=True)
    context_object_name = "products"
    template_name = "kishore/store/product_list.html"
    paginate_by = 25
    paginator_class = KishorePaginator

class ProductDetail(DetailView):
    queryset = Product.objects.filter(visible=True)
    context_object_name = "product"
    template_name = "kishore/store/product_detail.html"

class ProductsByTag(ListView):
    model = Product
    context_object_name = "products"
    template_name = "kishore/store/product_list.html"
    paginate_by = 25
    paginator_class = KishorePaginator

    def get_queryset(self):
        return Product.objects.filter(tags__slug__in=[self.kwargs['tag']],visible=True)

    def get_context_data(self, **kwargs):
        context = super(ProductsByTag, self).get_context_data(**kwargs)
        tag = get_object_or_404(Tag, slug=self.kwargs['tag'])
        context['title'] = "Products tagged %s" % tag.name
        return context

def cart(request):
    cart = utils.get_or_create_cart(request)
    return render(request, "kishore/store/cart.html", {'cart': cart})

def add_to_cart(request):
    if request.method == "POST":
        cart = utils.get_or_create_cart(request)
        form = CartItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)

            cart_items = cart.cartitem_set.filter(product=item.product)
            # check to see we don't already have this product in the cart
            if len(cart_items) > 0:
                item_to_update = cart_items[0]
                item_to_update.quantity = item_to_update.quantity + item.quantity
                item_to_update.save()
            else:
                item.cart = cart
                item.save()

        return redirect("kishore_cart")
    else:
        return HttpResponse("Bad request", status=400)

def update_cart(request, item_id):
    if request.method == "POST":
        cart = utils.get_or_create_cart(request)
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
        cart = utils.get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id)

        if item not in cart.cartitem_set.all():
            return HttpResponse("Bad request", status=400)

        item.delete()
        return redirect("kishore_cart")
    else:
        return HttpResponse("Bad request", status=400)

def checkout(request):
    cart = utils.get_or_create_cart(request)
    valid = cart.clean()

    if not valid:
        return render(request, "kishore/store/cart.html", {'cart':cart,'error':True})
    if cart.empty:
        return redirect("kishore_cart")
    elif cart.shippable:
        return redirect('kishore_shipping')
    else:
        request.session['kishore_order_id'] = None
        return redirect('kishore_payment')

def shipping(request):
    backend = utils.load_class(kishore_settings.KISHORE_SHIPPING_BACKEND)()
    return backend.shipping_view(request)

def shipping_methods(request):
    backend = utils.load_class(kishore_settings.KISHORE_SHIPPING_BACKEND)()
    return backend.shipping_method_view(request)

def payment(request):
    order = utils.get_or_create_order(request)

    if request.method == "POST":
        form = PaymentForm(request.POST, order=order)
        if form.is_valid():
            order.customer_name = form.cleaned_data['name']
            order.customer_email = form.cleaned_data['email']
            order.payment_processor = form.cleaned_data['processor']
            order.save()

            p = form.cleaned_data["processor"]
            klass = utils.load_class(p)
            processor = klass(order)
            return processor.get_response(request)
    else:
        cart = utils.get_or_create_cart(request)
        order.prepare_from_cart(cart)
        form = PaymentForm(order=order)

    return render(request, "kishore/store/payment.html",{'form':form,'order':order})

def process_payment(request):
    order = utils.get_or_create_order(request)

    if order.total == 0:
        return redirect("kishore_store")

    klass = utils.load_class(order.payment_processor)
    payment_processor = klass(order)
    valid = payment_processor.accept_payment(request)

    if valid:
        order.complete()
        utils.clear_session_vars(request)
        return render(request, "kishore/store/success.html",{'order':order})
    else:
        error = "We're sorry, there was a problem charging you, please try again."
        return render(request, "kishore/store/error.html",{'error':error})

SHA1_RE = re.compile('^[a-f0-9]{40}$')

def _validate_key(download_key):
    download_key = download_key.lower()

    if not SHA1_RE.search(download_key):
        return (False, None)

    try:
        link = DownloadLink.objects.get(key=download_key)
    except ObjectDoesNotExist:
        return (False, None)

    if not link.active:
        return (False, None)

    if link.first_accessed:
        if timezone.now() - link.first_accessed > timedelta(hours=6):
            link.active = False
            link.save()
            return (False, None)

    return (True, link)

def download(request, download_key):
    valid, link = _validate_key(download_key)

    if not valid:
        return render(request, 'kishore/store/download.html',{'error': True})
    else:
        request.session['kishore_download_key'] = download_key

        product = link.item.product

        download_urls = []
        for release in link.find_releases():
            download_urls.append(
                {'name': release.__unicode__,
                 'url': reverse(
                        'kishore_process_download',
                        kwargs={'download_key': download_key,'product_id': release.pk})
                 })

        return render(request, 'kishore/store/download.html', {'download_urls': download_urls})

def process_download(request, download_key, product_id):
    valid, link = _validate_key(download_key)

    if not link.first_accessed:
        link.first_accessed = timezone.now()
        link.save()

    if not valid:
        return render(request, 'store/download.html',{'error': True})
    else:
        releases = link.find_releases()
        if len(releases) > 1:
            releases = releases.filter(pk=product_id)

        release = releases[0]
        return redirect(release.get_download_url())

class BuyNow(View):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])

        # create an empty cart and add a single item
        cart = utils.get_or_create_cart(request, force_create=True)
        cart.add_product(product)

        return redirect("kishore_checkout")
