from django.conf import settings

# DEFAULT SETTINGS
KISHORE_CURRENCY = getattr(settings, "KISHORE_CURRENCY", "usd")
KISHORE_CURRENCY_SYMBOL = getattr(settings, "KISHORE_CURRENCY_SYMBOL", "$")

KISHORE_AUDIO_PLAYER = getattr(settings, "KISHORE_AUDIO_PLAYER", "kishore.models.SoundcloudPlayer")

KISHORE_LABEL_LAYOUT = getattr(settings, "KISHORE_LABEL_LAYOUT", False)

KISHORE_STYLESHEETS = getattr(settings, "KISHORE_STYLESHEETS",
                              ["kishore/css/styles.css", "kishore/css/default.css"])

KISHORE_JAVASCRIPT = getattr(settings, "KISHORE_JAVASCRIPT",
                             ["kishore/js/jquery-1.9.1.min.js",
                              "kishore/js/mustache.js",
                              "kishore/js/scripts.js"])

KISHORE_ADMIN_STYLESHEETS = getattr(settings, "KISHORE_ADMIN_STYLESHEETS",
                                    ["kishore/css/admin/bootstrap.css",
                                     "kishore/css/admin/admin.css"])

KISHORE_ADMIN_JAVASCRIPT = getattr(settings, "KISHORE_JAVASCRIPT",
                                   ["kishore/js/jquery-1.9.1.min.js",
                                    "kishore/js/mustache.js",
                                    "kishore/js/admin/admin.js"])

KISHORE_PAYMENT_BACKENDS = getattr(settings, "KISHORE_PAYMENT_BACKENDS",
                                   ["kishore.payment.StripeBackend",
                                    "kishore.payment.PaypalBackend"])

KISHORE_SHIPPING_BACKEND = getattr(settings, "KISHORE_SHIPPING_BACKEND",
                                   "kishore.shipping.EasyPostBackend")

KISHORE_STORAGE_BACKEND = getattr(settings, "KISHORE_STORAGE_BACKEND",
                                  "kishore.storage.SecureS3Storage")

KISHORE_FROM_EMAIL = getattr(settings, "KISHORE_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)
KISHORE_SUPPORT_EMAIL = getattr(settings, "KISHORE_SUPPORT_EMAIL", KISHORE_FROM_EMAIL)

TAX_RATES = {
    'AL': 0.04,
    'AK': 0,
    'AZ': 0.056,
    'AR': 0.065,
    'CA':0.075,
    'CO': 0.029,
    'CT': 0.0635,
    'DE': 0,
    'DC': 0.06,
    'FL': 0.06,
    'GA': 0.04,
    'HI': 0.04,
    'ID': 0.06,
    'IL': 0.0625,
    'IN': 0.07,
    'IA': 0.06,
    'KS': 0.0615,
    'KY': 0.06,
    'LA': 0.04,
    'ME': 0.05,
    'MD': 0.06,
    'MA': 0.0625,
    'MI': 0.06,
    'MN': 0.06875,
    'MS': 0.07,
    'MO': 0.04225,
    'MT': 0,
    'NE': 0.055,
    'NV': 0.0685,
    'NH': 0,
    'NJ': 0.07,
    'NM': 0.05125,
    'NY': 0.04,
    'NC': 0.04750,
    'ND': 0.05,
    'OH': 0.055,
    'OK': 0.045,
    'OR': 0,
    'PA': 0.06,
    'RI': 0.07,
    'SC': 0.06,
    'SD': 0.04,
    'TN': 0.07,
    'TX': 0.0625,
    'UT': 0.047,
    'VT': 0.06,
    'VA': 0.043,
    'WA': 0.065,
    'WV': 0.06,
    'WI': 0.05,
    'WY': 0.04,
    }

KISHORE_TAX_RATES = getattr(settings, "KISHORE_TAX_RATES", TAX_RATES)
