from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)

from . import forms, models, clashapi, filters

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
    paginate_by = 60

    def get_queryset(self):
        queryset = super().get_queryset()
        return filters.ClanMemberFilter(self.request.GET, queryset=queryset).qs
    #     filter_val = self.request.GET.get('filter', 'all')

    #     # if filter_val == 'all':
    #     #     self.paginate_by = 50
    #     #     return models.ClanMember.objects.all()
    #     # else:
        
    #     new_context = models.ClanMember.objects.filter(
    #             name="UZP I Simao",
    #         )

    #     return new_context


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clans'] = models.Clan.objects.all()
        context['totalSize'] = len(self.get_queryset())
        context['filter'] = filters.ClanMemberFilter(self.request.GET, queryset=self.get_queryset())

        return context

class ListClanHistory(generic.ListView):
    model = models.ClanMemberHistory
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return filters.ClanHistoryFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = filters.ClanHistoryFilter(self.request.GET, queryset=self.get_queryset())
        return context


@login_required
def changeClan(request, pk, newclan, currentfilter):
    member = get_object_or_404(models.ClanMember, pk=pk)
    clan = get_object_or_404(models.Clan, pk=newclan)
    member.changeClan(clan)
    return redirect('/clashdata/memberList/?filter=' + currentfilter)

def missingMembers(request):
    selectedClanId = request.GET.get('clan_filter_who_is_out', None)
    clans = models.Clan.objects.all()

    if selectedClanId is None:
        return render(request, "clashdata/whoisout.html", {'clans': clans, 'sel_clan_id': selectedClanId})
    else:
        try:
            clanTag = get_object_or_404(models.Clan, pk=selectedClanId)
            currentMembers = clashapi.getClanMembers(clanTag)
            print(currentMembers)
        except Exception as error:
            print(error.args)
            return render(request, "clashdata/whoisout.html", {'clans': clans, 'error': error.args, 'sel_clan_id': selectedClanId})
        
        missingMembers = []
        exceededMembers = []
        line = models.ClanMember.objects.values('tag', 'name').filter(clan=selectedClanId)

        for expectedMember in line:
            found = [x for x in currentMembers if x["tag"] == expectedMember["tag"]]
            if len(found) == 0:
                missingMembers.append({"name": expectedMember["name"], "tag": expectedMember["tag"]})

        for member in currentMembers:
            found = [x for x in line if x["tag"] == member["tag"]]
            if len(found) == 0:
                exceededMembers.append({"name": member["name"], "tag": member["tag"]})

        return render(request, "clashdata/whoisout.html", {'missing_members': missingMembers, 'exceeded_members': exceededMembers, 
                                                                                'clans': clans, 'sel_clan_id': selectedClanId, 
                                                                                'total_line': line.count(), 'total_clan': len(currentMembers)})



