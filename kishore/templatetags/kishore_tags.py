from django import template

from kishore import settings

register = template.Library()

@register.filter
def kishore_currency(value):
    return "%s%0.2f" % (settings.KISHORE_CURRENCY_SYMBOL, value)
