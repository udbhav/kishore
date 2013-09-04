Installation
============

1. Install django-kishore::

    pip install django-kishore

2. Create a new Django project if you don't already have one::

    django-admin.py startproject example

3. Make sure you have the following in INSTALLED_APPS in settings.py::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.contenttypes',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.humanize',
        'django.contrib.markup',
        'kishore'
    )

4. Run syncdb to create the database tables::

    python manage.py syncdb

5. Add Kishore's URLs to urls.py::

    from kishore.urls import music as music_urls, store as store_urls, admin as admin_urls

    urlpatterns = patterns('',
        (r'^music/', include(music_urls)),
        (r'^store/', include(store_urls)),
        (r'^manage/', include(admin_urls)),
    )

6. Install PIL::

   pip install pil

7. Configure the required settings :doc:`required settings <settings>`
