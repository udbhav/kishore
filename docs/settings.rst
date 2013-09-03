Settings
========

Important Kishore Settings
--------------------------

These settings all require various amounts of configuration on your part, depending on your choices

KISHORE_AUDIO_BACKENDS
~~~~~~~~~~~~~~~~~~~~~~

Default: ["kishore.models.SoundcloudPlayer","kishore.models.DefaultPlayer"]

An array of strings that are paths to classes to use as possible audio players.  If you plan on using
the built in Soundcloud player, you must set SOUNDCLOUD_CLIENT_ID, which you can get through
`Soundcloud <http://developers.soundcloud.com/>`_

KISHORE_LABEL_LAYOUT
~~~~~~~~~~~~~~~~~~~~

Default: True

If the site is for just a single artist, set this to False, and do the following to create the initial
artist data::

    python manage.py shell
    >>> from kishore.models import Artist
    >>> Artist.objects.create(name="Kishore Kumar")

KISHORE_PAYMENT_BACKENDS
~~~~~~~~~~~~~~~~~~~~~~~~

Default: ["kishore.payment.StripeBackend","kishore.payment.PaypalBackend"]

If you're using `Stripe <https://stripe.com/>`_, you must set STRIPE_SECRET_KEY and
STRIPE_PUBLISHABLE_KEY.


Required Django Settings
------------------------

There are a couple of Django specific settings you must have set for things to work.

LOGIN_URL
~~~~~~~~~

Set it to '/manage/accounts/login' if you mount Kishore's admin at '/manage'

TEMPLATE_CONTEXT_PROCESSORS
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Required, make sure it includes the kishore store and layout processors::

    TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'kishore.context_processors.store',
    'kishore.context_processors.layout',
    )

DEFAULT_FROM_EMAIL
~~~~~~~~~~~~~~~~~~

The address for emails sent from the store.


Optional Kishore Settings
-------------------------

Hooks to change other behavior

KISHORE_CURRENCY
~~~~~~~~~~~~~~~~

Default: "usd"

Used to determine what `currency codes <http://en.wikipedia.org/wiki/ISO_4217>`_ to use in when
processing payments.

KISHORE_CURRENCY_SYMBOL
~~~~~~~~~~~~~~~~~~~~~~~

Default: "$"

Used to change what's displayed in templates.

KISHORE_USE_LESS_FOR_CSS
~~~~~~~~~~~~~~~~~~~~~~~~

Default: False

If you want to customize the looks using less, set this to True, and install
`django-less <https://github.com/andreyfedoseev/django-less>`_.
