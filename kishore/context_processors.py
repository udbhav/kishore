from kishore import utils
from kishore import settings as kishore_settings

def store(request):
    cart = utils.get_or_create_cart(request)
    support_email = kishore_settings.KISHORE_SUPPORT_EMAIL
    return {'cart': cart, 'support_email': support_email}

def layout(request):
    return {'kishore_label_layout': kishore_settings.KISHORE_LABEL_LAYOUT,
            'kishore_site_name': kishore_settings.KISHORE_SITE_NAME,
            }
