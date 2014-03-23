from datetime import datetime, date, timedelta
import random
import re
import json

from django.core.urlresolvers import reverse
from django.db import models
from django import forms
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.hashcompat import sha_constructor
from django.utils.encoding import smart_str
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify
from django.db.models import Sum, Count
from django.utils import timezone

from kishore.templatetags.kishore_tags import kishore_currency
from kishore import settings as kishore_settings
from kishore import utils

from music import Song, Release
from image import Image, ModelFormWithImages
from cache import CachedModel
from tags import TaggableModel

PRODUCT_SUBCLASSES = [
    {"class": "DigitalSong", "name": "Digital Song"},
    {"class": "DigitalRelease", "name": "Digital Release"},
    {"class": "PhysicalRelease", "name": "Physical Release"},
    {"class": "Merch", "name": "Merch"},
    ]

class Product(CachedModel, TaggableModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2,
                                help_text="(%s) %s" % (kishore_settings.KISHORE_CURRENCY_SYMBOL,
                                                       kishore_settings.KISHORE_CURRENCY))
    description = models.TextField(blank=True)
    track_inventory = models.BooleanField()
    inventory = models.IntegerField(blank=True,null=True)
    images = models.ManyToManyField(Image, through='ProductImage', blank=True, null=True)
    visible = models.BooleanField(default=True)
    weight = models.IntegerField(help_text="(oz) an LP is usually 18oz, CD is 3oz",blank=True,null=True)

    def __unicode__(self):
        # return self.name
        return "%s (%s)" % (self.name, self.formatted_price)

    @property
    def subclass(self):
        for s in [x['class'].lower() for x in PRODUCT_SUBCLASSES]:
            if hasattr(self, s):
                return getattr(self, s)
        return None

    def get_subclass_name(self):
        if self.subclass:
            return [x["name"] for x in PRODUCT_SUBCLASSES if x["class"] == self.subclass.__class__.__name__][0]

    def get_absolute_url(self):
        return reverse('kishore_product_detail',kwargs={'slug':self.slug})

    def get_admin_url(self):
        return reverse('kishore_admin_product_update',kwargs={'pk':self.id})

    def get_cartitem_form(self):
        form = CartItemForm(instance=CartItem(product=self))
        form.fields["quantity"].widget = forms.HiddenInput()
        return form

    def get_description(self):
        if self.description:
            return self.description
        elif hasattr(self.subclass, 'get_related_description'):
            return self.subclass.get_related_description()

    def get_ordered_images(self):
        product_images = ProductImage.objects.filter(product=self).order_by('position')
        if product_images:
            return product_images
        elif hasattr(self.subclass, 'get_related_images'):
            return self.subclass.get_related_images()

    def get_primary_image(self):
        images = self.get_ordered_images()
        if len(images) > 0:
            return images[0].image

    def get_player_html(self):
        if hasattr(self.subclass, 'get_player_html'):
            return self.subclass.get_player_html()

    def get_related_music_object(self):
        if hasattr(self.subclass, 'release'):
            return self.subclass.release
        elif hasattr(self.subclass, 'song'):
            return self.subclass.song

    def get_artist(self):
        related = self.get_related_music_object()
        if related:
            return related.artist

    def get_cached_siblings(self):
        return [self.get_related_music_object()]

    @property
    def formatted_price(self):
        return kishore_currency(self.price)

    @property
    def in_stock(self):
        klass = self.subclass.__class__
        if (klass == PhysicalRelease or klass == Merch):
            if self.track_inventory and self.inventory <= 0:
                return False

        return True

    def ordered_images(self):
        return ProductImage.objects.filter(product=self).order_by('position')

    def images_as_json(self):
        return json.dumps([i.image.json_safe_values for i in self.ordered_images()])

    def save(self, *args, **kwargs):
        if not self.slug:
            valid_slug = False
            i = 0
            while not valid_slug:
                if i == 0:
                    proposed_slug = slugify(self.name)
                else:
                    proposed_slug = slugify("%s %s" % (self.name, i))
                try:
                    Product.objects.get(slug=proposed_slug)
                except ObjectDoesNotExist:
                    valid_slug = True
                else:
                    i += 1

            self.slug = proposed_slug

        super(Product, self).save(*args, **kwargs)

    class Meta:
        db_table = 'kishore_products'
        app_label = 'kishore'

class ProductImage(models.Model):
    product = models.ForeignKey(Product)
    image = models.ForeignKey('Image')
    position = models.IntegerField(default=1)

    class Meta:
        db_table = 'kishore_product_images'
        app_label = 'kishore'

class ProductForm(ModelFormWithImages):
    model_class = forms.ChoiceField(
        choices = [[x['class'], x['name']] for x in PRODUCT_SUBCLASSES],
        widget = forms.RadioSelect, label = "Product type",
        required = True)

    name = forms.CharField(required=False, widget=utils.KishoreTextInput)
    song = forms.ModelChoiceField(queryset=Song.objects.all(),
                                  widget=utils.KishoreSelectWidget,
                                  required=False)
    release = forms.ModelChoiceField(queryset=Release.objects.all(),
                                     widget=utils.KishoreSelectWidget,
                                     required=False
                                     )
    zipfile = forms.FileField(required=False, label="Zip file")
    product_images = forms.CharField(widget=forms.HiddenInput(attrs={'class':'kishore-images-input'}))
    images_field_name = 'product_images'
    object_id_name = 'product_id'
    through_model = ProductImage

    class Meta:
        model = Product
        exclude = ('images',)
        widgets = {
            'slug': utils.KishoreTextInput,
            'price': utils.KishoreTextInput,
            'inventory': utils.KishoreTextInput,
            'weight': utils.KishoreTextInput,
            'tags': utils.KishoreTagWidget(),
            'description': forms.Textarea(attrs={'class':'kishore-editor-input'})
            }

    def __init__(self, *args, **kwargs):
        # if there is an instance of product and a subclass, replace product with the subclass
        if 'instance' in kwargs and getattr(kwargs['instance'], 'subclass'):
            kwargs['instance'] = kwargs['instance'].subclass

        super(ProductForm, self).__init__(*args, **kwargs)

        # if we have a subclass, no need to show the product type radios
        if getattr(self.instance, 'subclass'):
            self.fields['model_class'].widget = forms.HiddenInput()
            self.fields['model_class'].initial = self.instance.subclass.__class__.__name__

    def clean(self):
        data = self.cleaned_data
        model_class = data.get('model_class')

        if not getattr(self.instance, 'subclass') and model_class:
            self.instance = eval(model_class)()

        if model_class:
            klass = eval(model_class)

            if klass == PhysicalRelease or klass == Merch:
                if not data['weight']:
                    self._errors['weight'] = self.error_class(["Weight is required"])

            if klass == DigitalRelease:
                if not data['zipfile']:
                    self._errors['zipfile'] = self.error_class(["Zipfile is required"])

            if klass == PhysicalRelease or klass == DigitalRelease:
                release = data['release']

                if not release:
                    self._errors['release'] = self.error_class(["Release is required"])

                if release and not data['name']:
                    data['name'] = release.title

            if klass == DigitalSong:
                song = data['song']

                if not song:
                    self._errors['song'] = self.error_class(["Song is required"])

                if song and not getattr(song, 'audio_file'):
                    self._errors['song'] = self.error_class(["Please choose a song that has an audio file"])
                if song and not data['name']:
                    data['name'] = song.title

            if not data['name']:
                self._errors['name'] = self.error_class(["Name is required"])

        elif not name:
            self._errors['name'] = self.error_class(["Name is required"])

        return data

class DigitalSong(Product):
    song = models.ForeignKey(Song, blank=True, null=True)
    shippable = False
    downloadable = True

    def get_download_url(self):
        return self.song.audio_file.storage.download_url(self.song.audio_file.name)

    def get_related_description(self):
        return self.song.description

    def get_related_images(self):
        return self.song.ordered_images()

    def get_player_html(self):
        if self.song.streamable:
            return self.song.get_player_html()

    class Meta:
        db_table = 'kishore_digitalsongs'
        app_label = 'kishore'

class DigitalRelease(Product):
    release = models.ForeignKey(Release, blank=True, null=True)
    zipfile = models.FileField(upload_to='uploads/store',storage=utils.load_class(kishore_settings.KISHORE_STORAGE_BACKEND)())
    shippable = False
    downloadable = True

    def __unicode__(self, price=True):
        return "%s - %s (%s)" % (self.release, self.name, self.formatted_price)

    def get_download_url(self):
        return self.zipfile.storage.download_url(self.zipfile.name)

    def get_related_description(self):
        return self.release.description

    def get_related_images(self):
        return self.release.ordered_images()

    def get_player_html(self):
        if self.release.streamable:
            return self.release.get_player_html()

    class Meta:
        db_table = 'kishore_digitalreleases'
        app_label = 'kishore'

class PhysicalRelease(Product):
    release = models.ForeignKey(Release, blank=True, null=True)
    shippable = True
    downloadable = True

    def __unicode__(self):
        return "%s - %s (%s)" % (self.release, self.name, self.formatted_price)

    def get_related_description(self):
        return self.release.description

    def get_related_images(self):
        return self.release.ordered_images()

    def get_player_html(self):
        if self.release.streamable:
            return self.release.get_player_html()

    def includes_downloads(self):
        if self.release.digitalrelease_set.filter(visible=True).count() > 0:
            return True

    class Meta:
        db_table = 'kishore_physicalreleases'
        app_label = 'kishore'

class MerchVariant(models.Model):
    name = models.CharField(max_length=100)
    price_difference = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField(default=0)
    images = models.ManyToManyField(Image)

    class Meta:
        db_table = 'kishore_merchvariants'
        app_label = 'kishore'

class Merch(Product):
    variants = models.ManyToManyField(MerchVariant)
    shippable = True
    downloadable = False

    class Meta:
        db_table = 'kishore_merch'
        app_label = 'kishore'

class Address(models.Model):
    name = models.CharField(max_length=200)
    street_address = models.CharField(max_length=200)
    street_address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=20)

    @property
    def formatted_address(self):
        string = "%s\n%s\n" % (self.name, self.street_address)

        if self.street_address2:
            string += "%s\n" % self.street_address2

        string += "%s %s, %s %s" % (self.city, self.state, self.country,
                                    self.zipcode)

        return string

    def __unicode__(self):
        return self.formatted_address

    class Meta:
        db_table = 'kishore_address'
        app_label = 'kishore'

class Order(models.Model):
    customer_name = models.CharField(max_length=129,blank=True)
    customer_email = models.EmailField(blank=True)

    payment_processor = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100,blank=True)

    shipment_processor = models.CharField(max_length=100)
    shipment_id = models.CharField(max_length=50,blank=True)
    shipment_method_id = models.CharField(max_length=50,blank=True)
    shipping_address = models.ForeignKey(Address, blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    active = models.BooleanField()
    shipped = models.BooleanField()
    refunded = models.BooleanField()

    class Meta:
        db_table = 'kishore_orders'
        app_label = 'kishore'

    def __unicode__(self):
        return "#%i %s" % (self.id, self.customer_name)

    @classmethod
    def sales_data(self, start, end=timezone.now()):
        return self.objects.filter(
            timestamp__lte=end).filter(
            timestamp__gte=start).aggregate(total=Sum('subtotal'), count=Count('id'))

    @classmethod
    def sales_by_day(self, start=date.today()-timedelta(days=30), end=date.today()):
        day = start
        sales_data = []

        while day != end:
            sales_data.append({
                    'date': day,
                    'data': self.sales_data(day, day+timedelta(days=1))
                    })
            day = day + timedelta(days=1)

        return sales_data

    @property
    def total(self):
        return self.subtotal + self.shipping_total + self.tax

    @property
    def shippable(self):
        if self.shipment_processor:
            return True
        else:
            return False

    @property
    def waiting_to_ship(self):
        if self.shippable and not self.shipped:
            return True
        else:
            return False

    @property
    def downloadable(self):
        for item in self.orderitem_set.all():
            if item.downloadable:
                return True

    @property
    def processor_name(self):
        return self.get_payment_processor().human_name

    @property
    def formatted_shipping_address(self):
        if self.shipping_address:
            return self.shipping_address.formatted_address
        else:
            return ""

    def get_absolute_url(self):
        return reverse('kishore_admin_order_detail', kwargs={'pk':self.pk})

    def get_admin_url(self):
        return self.get_absolute_url()

    def prepare_from_cart(self, cart):
        # delete old order items
        self.orderitem_set.all().delete()

        subtotal = 0

        # create new ones
        for item in cart.cartitem_set.all():
            order_item = OrderItem.objects.create(
                order=self,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price)
            subtotal += item.quantity * item.unit_price

        self.subtotal = subtotal

        # taxes
        klass = utils.load_class(kishore_settings.KISHORE_TAX_BACKEND)
        tax_processor = klass(self)
        self.tax = tax_processor.calculate_tax()

        self.save()

    def complete(self):
        self.active = True

        for item in self.orderitem_set.all():
            item.create_download_links()
            item.decrement_product_inventory()

        self.send_confirmation_mail()
        self.save()

    def send_confirmation_mail(self):
        plaintext = get_template('kishore/store/order_confirmation_email.txt')
        html = get_template('kishore/store/order_confirmation_email.html')
        context = Context({ 'order': self })
        text_content = plaintext.render(context)
        html_content = html.render(context)
        msg = EmailMultiAlternatives(
            'Your Order', text_content, kishore_settings.KISHORE_FROM_EMAIL, [self.customer_email]
            )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def refund(self):
        processor = self.get_payment_processor()
        valid = processor.refund_order()

        if valid:
            self.refunded = True
            self.save()

    def get_payment_processor(self):
        klass = utils.load_class(self.payment_processor)
        return klass(self)

    def get_shippable_items(self):
        return [i for i in self.orderitem_set.all() if i.product.subclass.shippable]

class OrderItem(models.Model):
    order = models.ForeignKey('Order')
    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'kishore_orderitems'
        app_label = 'kishore'

    @property
    def price(self):
        return self.quantity * self.unit_price

    @property
    def downloadable(self):
        if self.product.subclass.downloadable:
            return True
        else:
            return False

    def create_download_links(self):
        if self.downloadable:
            i = self.quantity

            while i > 0:
                DownloadLink.objects.create(item=self)
                i += -1

    def decrement_product_inventory(self):
        if self.product.track_inventory:
            self.product.inventory -= self.quantity
            self.product.save()

class Cart(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.timestamp)

    def total_price(self):
        return sum([i.unit_price * i.quantity for i in self.cartitem_set.all()])

    @property
    def item_count(self):
        return sum([x.quantity for x in self.cartitem_set.all()])

    @property
    def total_weight(self):
        # total weight in oz
        return sum([x.product.weight for x in self.cartitem_set.all()])

    @property
    def shippable(self):
        for item in self.cartitem_set.all():
            if item.product.subclass.shippable:
                return True

        return False

    @property
    def empty(self):
        if self.cartitem_set.count() == 0:
            return True
        else:
            return False

    def clean(self):
        valid = True

        for item in self.cartitem_set.all():
            if item.product.track_inventory:
                if not item.product.in_stock:
                    valid = False
                    item.delete()
                elif item.quantity > item.product.inventory:
                    valid = False
                    item.quantity = item.product.inventory
                    item.save()

        return valid

    def add_product(self, product, quantity=1):
        # check to see we don't already have this product in the cart
        if self.cartitem_set.filter(product=product).count() > 0:
            item_to_update = self.cartitem_set.filter(product=product)[0]
            item_to_update.quantity = item_to_update.quantity + quantity
            item_to_update.save()
        else:
            CartItem.objects.create(cart=self,product=product,quantity=quantity)

    class Meta:
        db_table = 'kishore_carts'
        app_label = 'kishore'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __unicode__(self):
        return self.product.__unicode__()

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        super(CartItem, self).save(*args, **kwargs)

    def get_form(self):
        return CartItemForm(instance=self)

    class Meta:
        db_table = 'kishore_cartitems'
        app_label = 'kishore'

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        exclude = ("cart","unit_price")
        widgets = {'product': forms.HiddenInput(),
                   'quantity': forms.TextInput(attrs={'class':'form-control'})}

    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        if data < 1:
            data = 1
        return data



text_widget = forms.TextInput(attrs={'class': 'form-control'})

class PaymentForm(forms.Form):
    name = forms.CharField(max_length=100, widget=text_widget)
    email = forms.EmailField(widget=text_widget)
    #processor = forms.ChoiceField(choices=PAYMENT_PROCESSORS, label="Pay with", widget=forms.RadioSelect, initial=PAYMENT_PROCESSORS[0][0])

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop("order", None)
        self.choices = self._choices()

        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['processor'] = forms.ChoiceField(choices=self.choices,
                                                     label="Pay with",
                                                     widget=forms.RadioSelect,
                                                     initial=self.choices[0][0])

    def _choices(self):
        choices = []
        for backend in kishore_settings.KISHORE_PAYMENT_BACKENDS:
            processor = utils.load_class(backend)(self.order)
            if processor.valid:
                choices.append([backend, processor.human_name, processor.priority])

        return [[x[0], x[1]] for x in sorted(choices, key=lambda y: y[2])]

class DownloadLink(models.Model):
    item = models.ForeignKey(OrderItem)
    key = models.CharField(max_length=40, unique=True)
    active = models.BooleanField(default=True)
    first_accessed = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.item.__unicode__()

    def create_key(self):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        download_key = sha_constructor(salt+smart_str(self.item.product.__unicode__())).hexdigest()
        return download_key

    def get_full_url(self):
        url = reverse('kishore_download', kwargs= {'download_key': self.key})
        return('http://%s%s' % (Site.objects.get_current(), url))

    def save(self, *args, **kwargs):
        if not self.key:
            valid_key = False

            while not valid_key:
                proposed_key = self.create_key()
                try:
                    DownloadLink.objects.get(key=proposed_key)
                except ObjectDoesNotExist:
                    valid_key = True

            self.key = proposed_key

        super(DownloadLink, self).save(*args, **kwargs)

    def find_releases(self):
        product = self.item.product
        if hasattr(product, 'physicalrelease'):
            return DigitalRelease.objects.filter(release=product.physicalrelease.release,visible=True)
        elif hasattr(product, 'digitalrelease'):
            return [product.digitalrelease]
        elif hasattr(product, 'digitalsong'):
            return [product.digitalsong]
        else:
            return []

    class Meta:
        db_table = 'kishore_downloadlinks'
        app_label = 'kishore'
