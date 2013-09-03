from django import template
from django.conf import settings
from django.forms import CheckboxInput, RadioSelect

from kishore import settings as kishore_settings

register = template.Library()

@register.filter
def kishore_currency(value):
    if not value:
        value = 0

    return "%s%0.2f" % (kishore_settings.KISHORE_CURRENCY_SYMBOL, float(value))

@register.simple_tag
def kishore_css():
    output = ""
    for path in kishore_settings.KISHORE_STYLESHEETS:
        output += "<link rel=\"stylesheet\" media=\"all\" href=\"%s%s\" />" % (settings.STATIC_URL, path)
    return output

@register.simple_tag
def kishore_js():
    output = ""
    for path in kishore_settings.KISHORE_JAVASCRIPT:
        output += "<script type=\"text/javascript\" src=\"%s%s\"></script>" % (settings.STATIC_URL, path)
    return output

@register.inclusion_tag('kishore/admin/pagination.html')
def kishore_pagination(page):
    return {
        'page': page,
        'previous': page.paginator.get_previous_range(page),
        'next': page.paginator.get_next_range(page),
        }

@register.filter(name='is_checkbox')
def is_checkbox(field):
  return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__

@register.filter(name='is_radio')
def is_radio(field):
  return field.field.widget.__class__.__name__ == RadioSelect().__class__.__name__
