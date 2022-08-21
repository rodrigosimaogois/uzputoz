from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from . import models
from django import forms

class ClanCreateForm(forms.ModelForm):
    class Meta:
        fields = ("name", "tag")
        model = models.Clan

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Nome'

class ClanMemberCreateForm(forms.ModelForm):
    class Meta:
        fields = ("name", "tag", "clan", "cargo", "media")
        model = models.ClanMember

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Nome'
        self.fields['clan'].label = 'Clã'
        