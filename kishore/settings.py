from django.conf import settings

# DEFAULT SETTINGS
KISHORE_CURRENCY_SYMBOL = getattr(settings, "KISHORE_CURRENCY_SYMBOL", "$")
KISHORE_AUDIO_PLAYER = getattr(settings, "KISHORE_AUDIO_PLAYER", "kishore.models.SoundcloudPlayer")
KISHORE_LAYOUT = getattr(settings, "KISHORE_LAYOUT", "band")
