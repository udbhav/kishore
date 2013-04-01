from datetime import datetime

from django.db import models
from django import forms

from products import Product

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

    class Meta:
        db_table = 'kishore_carts'
        app_label = 'kishore'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'kishore_cartitems'
        app_label = 'kishore'

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        exclude = ("cart","unit_price")
