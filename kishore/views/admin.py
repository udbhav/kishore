from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from kishore.models import Order, KishorePaginator, Artist, ArtistForm, Image, ImageForm
from kishore import utils

class OrderList(ListView):
    queryset = Order.objects.filter(active=True).order_by('-timestamp')
    template_name = "kishore/admin/order_list.html"
    context_object_name = "orders"
    paginate_by = 25
    paginator_class = KishorePaginator

class OrderDetail(DetailView):
    queryset = Order.objects.filter(active=True)
    template_name = "kishore/admin/order_detail.html"
    context_object_name = "order"

class ArtistAdminList(ListView):
    queryset = Artist.objects.all().order_by("name")
    template_name = "kishore/admin/artist_list.html"
    context_object_name = "artists"
    paginate_by = 25
    paginator_class = KishorePaginator

class ArtistCreate(CreateView):
    model = Artist
    form_class = ArtistForm
    template_name = "kishore/admin/create_artist.html"

    def get_success_url(self):
        return reverse("kishore_admin_artists")

class ArtistUpdate(UpdateView):
    model = Artist
    form_class = ArtistForm
    template_name = "kishore/admin/update_artist.html"

    def get_success_url(self):
        return reverse("kishore_admin_artists")

class ArtistDelete(DeleteView):
    model = Artist

    def get_success_url(self):
        return reverse("kishore_admin_artists")

class ImageList(ListView):
    model = Image
    template_name = "kishore/admin/image_list.html"
    context_object_name = "images"
    paginate_by = 21
    paginator_class = KishorePaginator

class ImageCreate(CreateView):
    model = Image
    form_class = ImageForm
    template_name = "kishore/admin/create_image.html"

    def get_success_url(self):
        return reverse("kishore_admin_images")

class ImageUpdate(UpdateView):
    model = Image
    form_class = ImageForm
    template_name = "kishore/admin/update_image.html"
    context_object_name = "image"

    def get_success_url(self):
        return reverse("kishore_admin_images")

class ImageDelete(DeleteView):
    model = Image

    def get_success_url(self):
        return reverse("kishore_admin_images")

@login_required
def dashboard(request):
    return render(request, "kishore/admin/index.html")

@login_required
def ship_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not order.shippable:
        return redirect("kishore_admin_dashboard")
    else:
        processor = utils.load_class(order.shipment_processor)()
        return processor.ship_order_view(request,order)

@login_required
def refund_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        order.refund()
        return redirect(order)
    else:
        return HttpResponse("Bad request", status=400)

@login_required
def hide_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        order.active = False
        order.save()
        return redirect("kishore_admin_orders")
    else:
        return HttpResponse("Bad request", status=400)

@login_required
def new_artist(request):
    if request.method == "POST":
        form = ArtistForm(request.POST)

        if form.is_valid():
            artist = form.save()
            return redirect('kishore_admin_artist_detail', kwargs={'pk':artist.pk})
    else:
        form = ArtistForm()

    return render(request, "kishore/admin/new_artist.html", {'form':form})
