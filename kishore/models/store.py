from datetime import datetime

from django.core.urlresolvers import reverse
from music import Song, Release
from image import Image
from django.db import models
from django import forms

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    inventory = models.IntegerField(default=-1)
    images = models.ManyToManyField(Image, blank=True, null=True)
    visible = models.BooleanField(default=True)

    def __unicode__(self):
        if self.subclass:
            return self.subclass.__unicode__()
        else:
            return self.name

    @property
    def subclass(self):
        subclasses = ('digitalsong', 'digitalrelease', 'physicalrelease', 'merch')
        for s in subclasses:
            if hasattr(self, s):
                return getattr(self, s)
        return None

    def get_absolute_url(self):
        return reverse('kishore_product_detail',kwargs={'slug':self.slug})

    def get_cartitem_form(self):
        return CartItemForm(instance=CartItem(product=self))

    def formatted_price(self):
        return "%01.2f" % self.price

    class Meta:
        db_table = 'kishore_products'
        app_label = 'kishore'

class DigitalSong(Product):
    song = models.OneToOneField(Song)

    class Meta:
        db_table = 'kishore_digitalsongs'
        app_label = 'kishore'

class DigitalRelease(Product):
    release = models.ForeignKey(Release)
    zipfile = models.FileField(upload_to='uploads/store')

    def __unicode__(self):
        return "%s - %s" % (self.release, self.name)

    class Meta:
        db_table = 'kishore_digitalreleases'
        app_label = 'kishore'

class PhysicalRelease(Product):
    release = models.ForeignKey(Release)

    def __unicode__(self):
        return "%s - %s" % (self.release, self.name)

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

    class Meta:
        db_table = 'kishore_merch'
        app_label = 'kishore'

STATUS_CHOICES = (
    ('w', 'Waiting for Payment'),
    ('u', 'Unreleased'),
    ('rs', 'Ready To Ship'),
    ('sn', 'Shipped No Digital'),
    ('ud', 'Unshipped Digital'),
    ('s', 'Shipped'),
    ('c', 'Complete'),
)

class Order(models.Model):
    customer_name = models.CharField(max_length=129)
    customer_email = models.EmailField()
    processor = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    shipping_address = models.TextField(blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, blank=True)

    def _unicode__(self):
        return self.customer_name

class OrderItem(models.Model):
    order = models.ForeignKey('Order')
    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

class Cart(models.Model):
    timestamp = models.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return str(self.timestamp)

    def total_price(self):
        return sum([i.unit_price * i.quantity for i in self.cartitem_set.all()])

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
        widgets = {'product': forms.HiddenInput()}

    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        if data < 1:
            data = 1
        return data
