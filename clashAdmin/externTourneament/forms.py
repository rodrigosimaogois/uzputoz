from django import forms  
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth.models import User
from django.forms import HiddenInput, ValidationError
from .models import RegisteredPlayers
from typing import Any
from . import models
import re
from clashdata import clashapi
  
class RegisteredPlayerForm(forms.ModelForm):
    class Meta:
        fields = ('nickname', 'tag', 'email', 'whatsapp')
        model = RegisteredPlayers

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['nickname'].widget = HiddenInput()
        self.fields['nickname'].initial = "-"
        self.fields['tag'].label = 'Tag'
        self.fields['email'].label = 'Email'
        self.fields['whatsapp'].label = 'WhatsApp (ex +5511971213334)'

    def clean(self):
        super(RegisteredPlayerForm, self).clean()

        self.cleaned_data['tag'] = self.cleaned_data['tag'].upper()

        tag = self.cleaned_data.get('tag')
        if not tag.startswith('#'):
            self._errors['tag'] = self.error_class(['Tag deve começar com #'])
        else:
            playerInfo = clashapi.getPlayerInfo(tag)
            name = playerInfo["name"]

            if name == "":
                self._errors['tag'] = self.error_class(['Tag inválida'])
            else:
                self.cleaned_data['nickname'] = name

        email = self.cleaned_data.get('email')
        player_qs = models.RegisteredPlayers.objects.values().filter(email=email)
   
        if len(player_qs) > 0:
            self._errors['email'] = self.error_class(['Email já registrado'])

        whatsapp = self.cleaned_data.get('whatsapp')

        validate_phone_number_pattern = "^\\+?[1-9][0-9]{7,14}$"
        if re.match(validate_phone_number_pattern, whatsapp) is None:
            self._errors['whatsapp'] = self.error_class(['Use apenas números e opcionalmente +. Exemplo: +5511971112222'])

        return self.cleaned_data