from base64 import urlsafe_b64decode, urlsafe_b64encode
from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)

from . import forms
from . import models
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
  

class RegisterParticipantView(generic.CreateView):

    def get(self, request, *args, **kwargs):
        context = {'form': forms.RegisteredPlayerForm()}
        return render(request, 'externTourneament/register_form.html', context)

    def post(self, request, *args, **kwargs):
        form = forms.RegisteredPlayerForm(request.POST)
        if form.is_valid():
            registered = form.save()
            registered.save()
            return render(request, 'externTourneament/confirmRegistration.html', {'msg': 'Obrigado pela inscrição !!!'})

            # token = str(registered.pk) + str(registered.tag)
            # token_bytes = token.encode('ascii')
            # b64 = urlsafe_b64encode(token_bytes)
            
            # #to get the domain of the current site  
            # current_site = get_current_site(request)
            # mail_subject = 'Link de confirmação'  
                
            # message = render_to_string('externTourneament/email.html', {  
            #     'domain': current_site.domain,  
            #     'token': b64.decode('ascii')
            # })  

            #email = EmailMessage(mail_subject, message, to=[registered.email])  
            #email.send() 

            #return HttpResponseRedirect(reverse_lazy('externTourneament:email', kwargs={'to': registered.email}))
        return render(request, 'externTourneament/register_form.html', {'form': form})

def confirm(request, token):
    try:
        res = urlsafe_b64decode(token)
        uid = res.decode('ascii')
        hash = uid.index('#')
        registeredId = uid[:hash]
        print(registeredId)
        registered = models.RegisteredPlayers.objects.get(pk=registeredId)
    except(Exception):
        registered = None
    
    if registered is not None:
        registered.confirmed = True
        registered.save()
        return render(request, 'externTourneament/confirmRegistration.html', {'msg': 'Obrigado pela inscrição !!!'})
    else:
        return render(request, 'externTourneament/confirmRegistration.html', {'msg': 'Erro na validação !!! Entre em contato com torneiogladiadores@gmail.com'})    
    
def email(request, to):
    context = {'to': to}
    return render(request, 'externTourneament/emailSent.html', context) 