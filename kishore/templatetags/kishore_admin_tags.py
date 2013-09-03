from django import template
from django.conf import settings
from kishore import settings as kishore_settings

register = template.Library()

@register.simple_tag
def kishore_admin_js():
    output = ""
    for path in kishore_settings.KISHORE_ADMIN_JAVASCRIPT:
        output += "<script type=\"text/javascript\" src=\"%s%s\"></script>" % (settings.STATIC_URL, path)
    return output
