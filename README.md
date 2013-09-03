Kishore
=======

Kishore is a [Django](http://www.djangoproject.com) application aimed at helping bands and record labels share and sell their music.

## Installation

1. Install django-kishore

    pip install django-kishore

2. Create a new Django project if you don't already have one.

    django-admin.py startproject example

3. Make sure you have the following in INSTALLED_APPS in settings.py:

    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'kishore'