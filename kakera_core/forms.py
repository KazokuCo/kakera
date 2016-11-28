from django import forms
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailusers.forms import UserEditForm, UserCreationForm

class UserEditForm(UserEditForm):
    bio = forms.CharField(widget=forms.Textarea, required=False, label=_("Bio"))
    twitter = forms.CharField(required=False, label=_("Twitter"))
