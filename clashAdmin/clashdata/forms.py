from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from . import models
from django import forms
from django.forms import HiddenInput
from . import clashapi

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

class ClanBRCreateForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'tag')
        model = models.ClanBR

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = HiddenInput()
        self.fields['name'].initial = "-"
        self.fields['tag'].label = 'Tag'

    def clean(self):
        super(ClanBRCreateForm, self).clean()

        self.cleaned_data['tag'] = self.cleaned_data['tag'].upper()

        tag = self.cleaned_data.get('tag')
        if not tag.startswith('#'):
            self._errors['tag'] = self.error_class(['Tag deve começar com #'])
        else:
            clanInfo = clashapi.getClanData(tag)
            name = clanInfo["name"]
            
            if name == "":
                self._errors['tag'] = self.error_class(['Tag inválida'])
            else:
                self.cleaned_data['name'] = name            

        return self.cleaned_data
        