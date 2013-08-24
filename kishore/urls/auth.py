from django.conf.urls import patterns, url

from kishore.models import KishoreAuthenticationForm, KishorePasswordResetForm, KishoreSetPasswordForm

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'kishore/auth/login.html','authentication_form': KishoreAuthenticationForm}, name='kishore_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'kishore/auth/logout.html'}, name='kishore_logout'),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change',
        {'template_name': 'kishore/auth/password_change_form.html'}, name='kishore_password_change'),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done',
        {'template_name': 'kishore/auth/password_change_done.html'},
        name='kishore_password_change_done'),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset',
        {'template_name': 'kishore/auth/password_reset_form.html',
         'password_reset_form': KishorePasswordResetForm,
         }, name='kishore_password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done',
        {'template_name': 'kishore/auth/password_reset_done.html'}, name='kishore_password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'kishore/auth/password_reset_confirm.html',
         'set_password_form': KishoreSetPasswordForm,
         }, name='kishore_password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'kishore/auth/password_reset_complete.html'}, name='kishore_password_reset_complete'),
)
