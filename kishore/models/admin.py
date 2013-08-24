from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django import forms
from django.core.paginator import Paginator

from kishore.utils import KishoreTextInput

class KishoreAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=KishoreTextInput(
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
    email = forms.EmailField(max_length=254, widget=KishoreTextInput(
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
