from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, View
from django.views.generic.list import BaseListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from kishore.models import (Order, KishorePaginator, Artist, ArtistForm, Image, ImageForm, Song,
                            SongForm, Release, ReleaseForm, UserForm, KishoreUserCreationForm,
                            Product, ProductForm, KishoreSearchForm, ProductSearchForm,
                            ArtistSearchForm, SongSearchForm, ReleaseSearchForm, OrderSearchForm,
                            ImageSearchForm)

from kishore import utils

class ProtectedView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedView, self).dispatch(*args, **kwargs)

class StaffView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_staff:
            return super(StaffView, self).dispatch(*args, **kwargs)
        else:
            return HttpResponse("Unauthorized", status=401)

class AdminSearchView(ProtectedView, FormView):
    form_class = KishoreSearchForm
    template_name = "kishore/admin/search.html"

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(query=form.cleaned_data['q'],
                                                      results=form.search()))

class OrderList(ProtectedView, ListView):
    queryset = Order.objects.filter(active=True).order_by('-timestamp')
    template_name = "kishore/admin/order_list.html"
    context_object_name = "orders"
    paginate_by = 25
    paginator_class = KishorePaginator

class OrderDetail(ProtectedView, DetailView):
    queryset = Order.objects.filter(active=True)
    template_name = "kishore/admin/order_detail.html"
    context_object_name = "order"

class OrderSearch(AdminSearchView):
    form_class = OrderSearchForm

    def get_context_data(self, **kwargs):
        context = super(OrderSearch, self).get_context_data(**kwargs)
        context['title'] = 'Order Search'
        return context

class ArtistAdminList(ProtectedView, ListView):
    queryset = Artist.objects.all().order_by("name")
    template_name = "kishore/admin/artist_list.html"
    context_object_name = "artists"
    paginate_by = 25
    paginator_class = KishorePaginator

class ArtistCreate(ProtectedView, CreateView):
    model = Artist
    form_class = ArtistForm
    template_name = "kishore/admin/create_artist.html"

    def get_success_url(self):
        return reverse("kishore_admin_artists")

class ArtistUpdate(ProtectedView, UpdateView):
    model = Artist
    form_class = ArtistForm
    template_name = "kishore/admin/update_artist.html"

    def get_success_url(self):
        return reverse("kishore_admin_artists")

class ArtistDelete(ProtectedView, DeleteView):
    model = Artist

    def get_success_url(self):
        return reverse("kishore_admin_artists")

class ImageList(ProtectedView, ListView):
    model = Image
    template_name = "kishore/admin/image_list.html"
    context_object_name = "images"
    paginate_by = 20
    paginator_class = KishorePaginator

class ImageJSONList(ProtectedView, utils.JSONResponseMixin, BaseListView):
    model = Image
    template_name = "kishore/admin/image_list.html"
    context_object_name = "images"
    paginate_by = 20

class ImageCreate(ProtectedView, CreateView):
    model = Image
    form_class = ImageForm
    template_name = "kishore/admin/create_image.html"

    def get_success_url(self):
        return reverse("kishore_admin_images")

class ImageUpdate(ProtectedView, UpdateView):
    model = Image
    form_class = ImageForm
    template_name = "kishore/admin/update_image.html"
    context_object_name = "image"

    def get_success_url(self):
        return reverse("kishore_admin_images")

class ImageDelete(ProtectedView, DeleteView):
    model = Image

    def get_success_url(self):
        return reverse("kishore_admin_images")

class ImageSearch(AdminSearchView):
    form_class = ImageSearchForm

    def get_context_data(self, **kwargs):
        context = super(ImageSearch, self).get_context_data(**kwargs)
        context['title'] = 'Image Search'
        return context

class SongAdminList(ProtectedView, ListView):
    queryset = Song.objects.all().order_by("title")
    template_name = "kishore/admin/song_list.html"
    context_object_name = "songs"
    paginate_by = 25
    paginator_class = KishorePaginator

class SongCreate(ProtectedView, CreateView):
    model = Song
    form_class = SongForm
    template_name = "kishore/admin/create_song.html"

    def get_success_url(self):
        return reverse("kishore_admin_songs")

class SongUpdate(ProtectedView, UpdateView):
    model = Song
    form_class = SongForm
    template_name = "kishore/admin/update_song.html"

    def get_success_url(self):
        return reverse("kishore_admin_songs")

class SongDelete(ProtectedView, DeleteView):
    model = Song

    def get_success_url(self):
        return reverse("kishore_admin_songs")

class SongJSONList(ProtectedView, utils.JSONResponseMixin, BaseListView):
    model = Song
    paginate_by = 20

class ReleaseAdminList(ProtectedView, ListView):
    queryset = Release.objects.all().order_by("title")
    template_name = "kishore/admin/release_list.html"
    context_object_name = "releases"
    paginate_by = 25
    paginator_class = KishorePaginator

class ReleaseCreate(ProtectedView, CreateView):
    model = Release
    form_class = ReleaseForm
    template_name = "kishore/admin/create_release.html"

    def get_success_url(self):
        return reverse("kishore_admin_releases")

class ReleaseUpdate(ProtectedView, UpdateView):
    model = Release
    form_class = ReleaseForm
    template_name = "kishore/admin/update_release.html"

    def get_success_url(self):
        return reverse("kishore_admin_releases")

class ReleaseDelete(ProtectedView, DeleteView):
    model = Release

    def get_success_url(self):
        return reverse("kishore_admin_releases")

class UserList(StaffView, ListView):
    queryset = User.objects.all()
    template_name = "kishore/admin/user_list.html"
    context_object_name = "users"
    paginate_by = 25
    paginator_class = KishorePaginator

class UserCreate(StaffView, CreateView):
    model = User
    form_class = KishoreUserCreationForm
    template_name = "kishore/admin/create_user.html"

    def get_success_url(self):
        return reverse("kishore_admin_users")

class UserUpdate(StaffView, UpdateView):
    model = User
    form_class = UserForm
    template_name = "kishore/admin/update_user.html"

    def get_success_url(self):
        return reverse("kishore_admin_users")

class UserDelete(StaffView, DeleteView):
    model = User

    def get_success_url(self):
        return reverse("kishore_admin_users")

class ProductAdminList(ProtectedView, ListView):
    queryset = Product.objects.all()
    template_name = "kishore/admin/product_list.html"
    context_object_name = "products"
    paginate_by = 25
    paginator_class = KishorePaginator

class ProductCreate(ProtectedView, FormView):
    template_name = "kishore/admin/create_product.html"
    form_class = ProductForm

    def form_valid(self, form):
        form.save()
        return super(ProductCreate, self).form_valid(self)

    def get_success_url(self):
        return reverse("kishore_admin_products")

class ProductUpdate(ProtectedView, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "kishore/admin/update_product.html"

    def get_success_url(self):
        return reverse("kishore_admin_products")

class ProductDelete(ProtectedView, DeleteView):
    model = Product

    def get_success_url(self):
        return reverse("kishore_admin_products")

class ProductSearch(AdminSearchView):
    form_class = ProductSearchForm

    def get_context_data(self, **kwargs):
        context = super(ProductSearch, self).get_context_data(**kwargs)
        context['title'] = 'Product Search'
        return context

class ArtistSearch(AdminSearchView):
    form_class = ArtistSearchForm

    def get_context_data(self, **kwargs):
        context = super(ArtistSearch, self).get_context_data(**kwargs)
        context['title'] = 'Artist Search'
        return context

class ReleaseSearch(AdminSearchView):
    form_class = ReleaseSearchForm

    def get_context_data(self, **kwargs):
        context = super(ReleaseSearch, self).get_context_data(**kwargs)
        context['title'] = 'Release Search'
        return context

class SongSearch(AdminSearchView):
    form_class = SongSearchForm

    def get_context_data(self, **kwargs):
        context = super(SongSearch, self).get_context_data(**kwargs)
        context['title'] = 'Song Search'
        return context

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
