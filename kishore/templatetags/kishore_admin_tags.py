from django import template
from django.conf import settings
from kishore import settings as kishore_settings

try:
    from less.templatetags.less import less as less_tag
except ImportError:
    pass

register = template.Library()

@register.simple_tag
def kishore_admin_js():
    output = ""
    for path in kishore_settings.KISHORE_ADMIN_JAVASCRIPT:
        output += "<script type=\"text/javascript\" src=\"%s%s\"></script>" % (settings.STATIC_URL, path)
    return output

@register.simple_tag
def kishore_admin_css():
    if kishore_settings.KISHORE_USE_LESS_FOR_CSS:
        path = less_tag("kishore/css/admin.less")
    else:
        path = "kishore/css/admin.css"

    return "<link rel=\"stylesheet\" href=\"%s%s\" type=\"text/css\" />" % (settings.STATIC_URL, path)
