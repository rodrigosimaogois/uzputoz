from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)

from . import forms, models

import requests
import json

# Create your views here.

class CreateClan(LoginRequiredMixin, generic.CreateView):
    form_class = forms.ClanCreateForm
    success_url = reverse_lazy('clashdata:clans')
    template_name = 'clashdata/clan_form.html'

class DeleteClan(LoginRequiredMixin, generic.DeleteView):
    model = models.Clan
    success_url = reverse_lazy("clashdata:clans")
        
class UpdateClan(LoginRequiredMixin, generic.UpdateView):
    model = models.Clan
    form_class = forms.ClanCreateForm
    success_url = reverse_lazy('clashdata:clans')
    template_name = 'clashdata/clan_form.html'

class ListClans(generic.ListView):
    model = models.Clan

class CreateClanMember(LoginRequiredMixin, generic.CreateView):
    form_class = forms.ClanMemberCreateForm
    success_url = reverse_lazy('clashdata:members')
    template_name = 'clashdata/clanmember_form.html'

class UpdateClanMember(LoginRequiredMixin, generic.UpdateView):
    model = models.ClanMember
    form_class = forms.ClanMemberCreateForm
    success_url = reverse_lazy('clashdata:members')
    template_name = 'clashdata/clanmember_form.html'

class DeleteClanMember(LoginRequiredMixin, generic.DeleteView):
    model = models.ClanMember
    success_url = reverse_lazy("clashdata:members")

class ListMembers(generic.ListView):
    model = models.ClanMember
    
    def get_queryset(self):
        filter_val = self.request.GET.get('filter', 'all')

        if filter_val == 'all':
            self.paginate_by = 50
            return models.ClanMember.objects.all()
        else:
            new_context = models.ClanMember.objects.filter(
                clan=filter_val,
            )

            return new_context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        context['clans'] = models.Clan.objects.all()
        context['totalSize'] = self.get_queryset().count()
        
        return context

@login_required
def changeClan(request, pk, newclan, currentfilter):
    member = get_object_or_404(models.ClanMember, pk=pk)
    clan = get_object_or_404(models.Clan, pk=newclan)
    member.changeClan(clan)
    return redirect('/clashdata/memberList/?filter=' + currentfilter)

from datetime import datetime

class ListClanHistory(generic.ListView):
    model = models.ClanMemberHistory
    paginate_by = 50
    
    def get_queryset(self):
        return models.ClanMemberHistory.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def missingMembers(request):
    selectedClanId = request.GET.get('clan_filter_who_is_out', None)
    clans = models.Clan.objects.all()

    if selectedClanId is None:
        return render(request, "clashdata\whoisout.html", {'clans': clans})
    else:

        def callEndPoint(url):

            #api = models.RoyaleApiConfig.objects.all()

            headers = {
                        'Accept': 'application/json',
                        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjY4NjgyNDU1LThkOGMtNGQ4Ny1hZGFmLTE1ZjI4MDM1ZDIwOCIsImlhdCI6MTY1OTYyNzg5Mywic3ViIjoiZGV2ZWxvcGVyLzUwODc3ODg3LTdiZTktZGU3MC05MWNkLTkzOTNkY2M1ZWUyMiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3OC40Mi4xMDcuMTM4Il0sInR5cGUiOiJjbGllbnQifV19.lS1ECsYhV0OhscL4bAYvthg0UQiZgEHJBfID1TJKkGaG1fF8hpELXOjznM4Vd6qACegTqZ2X9QK6GG2KPD7X7Q'
                    }

            print(url)
            response = requests.get(url,headers=headers)

            if response.status_code != 200:
                print(f"error: {response.status_code}: {response._content}")
                
            return response.json()

        clanTag = get_object_or_404(models.Clan, pk=selectedClanId)
        tag = clanTag.tag.replace("#","")

        missingMembers = []
        currentMembers = callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/members")["items"]

        line = models.ClanMember.objects.values('tag', 'name').filter(clan=selectedClanId)

        for expectedMember in line:
            found = [x for x in currentMembers if x["tag"] == expectedMember["tag"]]
            if len(found) == 0:
                missingMembers.append({"name": expectedMember["name"], "tag": expectedMember["tag"]})

        return render(request, "clashdata\whoisout.html", {'missing_members': missingMembers, 'clans': clans})



