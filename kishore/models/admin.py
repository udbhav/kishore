import json

from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm, SetPasswordForm,
                                       UserCreationForm)
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import models

from kishore import utils

class KishoreAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=utils.KishoreTextInput(
            attrs = {
                'placeholder': 'Username',
                'autofocus': 'true',
                }))
    password = forms.CharField(widget=forms.PasswordInput(
            attrs = {
                'class': 'form-control',
                'placeholder': 'Password',
                }))

class KishorePasswordResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254, widget=utils.KishoreTextInput(
            attrs = {
                'placeholder': 'Email',
                'autofocus': 'true',
                'type': 'email',
                }
            ))

class KishoreSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(
            attrs = {
                'class': 'form-control',
                'placeholder': 'New Password',
                'autofocus': 'true',
                }
            ))
    new_password2 = forms.CharField(widget=forms.PasswordInput(
            attrs = {
                'class': 'form-control',
                'placeholder': 'Confirm Password',
                }
            ))

class KishorePaginator(Paginator):
    kishore_page_range = 5

    def get_previous_range(self, page):
        if page.number - self.kishore_page_range <= 0:
            return range(2,page.number)
        else:
            return range(page.number-self.kishore_page_range,page.number)

    def get_next_range(self, page):
        if page.number + self.kishore_page_range >= self.num_pages:
            return range(page.number + 1,self.num_pages)
        else:
            return range(page.number + 1,page.number + self.kishore_page_range + 1)

class KishoreUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(KishoreUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = utils.KishoreTextInput()
        self.fields['password1'].widget = utils.KishorePasswordInput()
        self.fields['password2'].widget = utils.KishorePasswordInput()


class UserForm(forms.ModelForm):
    username = forms.CharField(widget=utils.KishoreTextInput)
    class Meta:
        fields = ('username','is_staff')
        model = User
