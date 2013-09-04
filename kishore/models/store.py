from datetime import datetime
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

from kishore.templatetags.kishore_tags import kishore_currency
from kishore import settings as kishore_settings
from kishore import utils

from music import Song, Release, WithSlug
from image import Image, ModelFormWithImages

PRODUCT_SUBCLASSES = [
    {"class": "DigitalSong", "name": "Digital Song"},
    {"class": "DigitalRelease", "name": "Digital Release"},
    {"class": "PhysicalRelease", "name": "Physical Release"},
    {"class": "Merch", "name": "Merch"},
    ]

class Product(WithSlug):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    track_inventory = models.BooleanField()
    inventory = models.IntegerField(blank=True,null=True)
    images = models.ManyToManyField(Image, through='ProductImage', blank=True, null=True)
    visible = models.BooleanField(default=True)
    weight = models.IntegerField(help_text="(oz) an LP is usually 18oz, CD is 3oz",blank=True,null=True)

    def __unicode__(self):
        # return self.name
        return "%s (%s)" % (self.name, self.formatted_price)

    def name_with_no_price(self):
        return re.sub(r'\([^)]*\)', '', self.__unicode__())

    @property
    def subclass(self):
        for s in [x['class'].lower() for x in PRODUCT_SUBCLASSES]:
            if hasattr(self, s):
                return getattr(self, s)
        return None

    def get_subclass_name(self):
        return [x["name"] for x in PRODUCT_SUBCLASSES if x["class"] == self.subclass.__class__.__name__][0]

    def get_absolute_url(self):
        return reverse('kishore_product_detail',kwargs={'slug':self.slug})

    def get_cartitem_form(self):
        return CartItemForm(instance=CartItem(product=self))

    @property
    def formatted_price(self):
        return kishore_currency(self.price)

    def ordered_images(self):
        return ProductImage.objects.filter(product=self).order_by('position')

    def images_as_json(self):
        return json.dumps([i.image.json_safe_values for i in self.ordered_images()])

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
        widget = forms.RadioSelect, label = "Product type")

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
            'name': utils.KishoreTextInput,
            'slug': utils.KishoreTextInput,
            'price': utils.KishoreTextInput,
            'inventory': utils.KishoreTextInput,
            'weight': utils.KishoreTextInput,
            'description': forms.Textarea(attrs={'class':'kishore-editor-input'})
            }

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and getattr(kwargs['instance'], 'subclass'):
            kwargs['instance'] = kwargs['instance'].subclass

        super(ProductForm, self).__init__(*args, **kwargs)

        if getattr(self.instance, 'subclass'):
            self.fields['model_class'].widget = forms.HiddenInput()
            self.fields['model_class'].initial = self.instance.subclass.__class__.__name__

    def clean(self):
        if not getattr(self.instance, 'subclass'):
            self.instance = eval(self.cleaned_data['model_class'])()

        return self.cleaned_data

class DigitalSong(Product):
    song = models.OneToOneField(Song)
    shippable = False
    downloadable = True

    class Meta:
        db_table = 'kishore_digitalsongs'
        app_label = 'kishore'

    def get_download_url(self):
        return self.song.audio_file.storage.download_url(self.song.audio_file.name)

class DigitalRelease(Product):
    release = models.ForeignKey(Release)
    zipfile = models.FileField(upload_to='uploads/store',storage=utils.load_class(kishore_settings.KISHORE_STORAGE_BACKEND)())
    shippable = False
    downloadable = True

    def __unicode__(self, price=True):
        return "%s - %s (%s)" % (self.release, self.name, self.formatted_price)

    def get_download_url(self):
        return self.zipfile.storage.download_url(self.zipfile.name)

    class Meta:
        db_table = 'kishore_digitalreleases'
        app_label = 'kishore'

class PhysicalRelease(Product):
    release = models.ForeignKey(Release)
    shippable = True
    downloadable = True

    def __unicode__(self):
        return "%s - %s (%s)" % (self.release, self.name, self.formatted_price)

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

class Order(models.Model):
    customer_name = models.CharField(max_length=129,blank=True)
    customer_email = models.EmailField(blank=True)

    payment_processor = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100,blank=True)

    shipment_processor = models.CharField(max_length=100)
    shipment_id = models.CharField(max_length=50,blank=True)
    shipment_method_id = models.CharField(max_length=50,blank=True)
    shipping_address = models.TextField(blank=True)

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

    def _unicode__(self):
        return self.customer_name

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

    def get_absolute_url(self):
        return reverse('kishore_admin_order_detail', kwargs={'pk':self.pk})

    def add_from_cart(self, cart):
        for item in cart.cartitem_set.all():
            OrderItem.objects.create(
                order=self,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price)

            self.subtotal += item.quantity * item.unit_price

        self.save()

    def fulfill(self):
        self.active = True

        for item in self.orderitem_set.all():
            item.create_download_links()

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
        processor = utils.load_class(self.payment_processor)()
        processor.refund_order(self)
        self.refunded = True
        self.save()

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

class Cart(models.Model):
    timestamp = models.DateTimeField(default=datetime.now())

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
        widgets = {'product': forms.HiddenInput(), 'quantity': forms.HiddenInput()}

    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        if data < 1:
            data = 1
        return data

PAYMENT_PROCESSORS = [[x, utils.load_class(x).human_name] for x in kishore_settings.KISHORE_PAYMENT_BACKENDS]

text_widget = forms.TextInput(attrs={'class': 'form-control'})

class PaymentForm(forms.Form):
    name = forms.CharField(max_length=100, widget=text_widget)
    email = forms.EmailField(widget=text_widget)
    processor = forms.ChoiceField(choices=PAYMENT_PROCESSORS, label="Pay with", widget=forms.RadioSelect, initial=PAYMENT_PROCESSORS[0][0])

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
            return DigitalRelease.objects.filter(release=product.physicalrelease.release)
        elif hasattr(product, 'digitalrelease'):
            return [product.digitalrelease]
        elif hasattr(product, 'digitalsong'):
            return [product.digitalsong]
        else:
            return []

    class Meta:
        db_table = 'kishore_downloadlinks'
        app_label = 'kishore'
