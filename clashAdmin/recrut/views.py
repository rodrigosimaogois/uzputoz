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
from . import filters
  
class RegisterCandidateView(generic.CreateView):

    def get(self, request, *args, **kwargs):
        context = {'form': forms.CandidateForm()}
        return render(request, 'recrut/register_form.html', context)

    def post(self, request, *args, **kwargs):
        form = forms.CandidateForm(request.POST)
        if form.is_valid():
            registered = form.save()
            registered.save()
            return render(request, 'recrut/showMsg.html', {'msg': 'Obrigado !!! Em breve entraremos em contato via whatsapp'})

        return render(request, 'recrut/register_form.html', {'form': form})

class ListCandidates(LoginRequiredMixin,generic.ListView):
    model = models.Candidate
    paginate_by = 60

    def get_queryset(self):
        queryset = super().get_queryset()
        return filters.CandidateFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['totalSize'] = len(self.get_queryset())
        context['filter'] = filters.CandidateFilter(self.request.GET, queryset=self.get_queryset())
        return context

class DeleteCandidate(LoginRequiredMixin, generic.DeleteView):
    model = models.Candidate
    success_url = reverse_lazy("recrut:candidates")