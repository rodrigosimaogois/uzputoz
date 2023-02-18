from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)

from . import forms, models, clashapi, filters
from django.core import serializers
from django.http import HttpResponse

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

@login_required
def updateMemberNames(request):
    members = models.ClanMember.objects.all()

    for member in members:
        memberInfo = clashapi.getPlayerInfo(member.tag)
        nameInGame = memberInfo["name"]
        if nameInGame == "" or nameInGame == member.name:
            continue
        member.name = nameInGame
        member.save()

    return redirect('/clashdata/memberList/')

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
    return redirect('/clashdata/memberList/?' + currentfilter)

def changeOrAddToClan(name, tag, clan):
    member_qs = models.ClanMember.objects.values().filter(tag=tag)
    clan = get_object_or_404(models.Clan, pk=clan)

    if len(member_qs) > 0:
        member = get_object_or_404(models.ClanMember, tag=tag)
        member.changeClan(clan)
    else:
        newMember = models.ClanMember(clan=clan, name=name, tag=tag)
        newMember.save()

def missingMembers(request):
    
    if request.method == 'POST':
        name = request.POST.get('name', None)
        tag = request.POST.get('tag', None)
        clan = request.POST.get('clan', None)
        changeOrAddToClan(name, tag, clan)
    
    selectedClanId = request.GET.get('clan_filter_who_is_out', None)
    clans = models.Clan.objects.all()

    if selectedClanId is None:
        return render(request, "clashdata/whoisout.html", {'clans': clans, 'sel_clan_id': selectedClanId})
    else:
        try:
            clanTag = get_object_or_404(models.Clan, pk=selectedClanId)
            currentMembers = clashapi.getClanMembers(clanTag.tag)
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
                clan_qs = models.ClanMember.objects.values('clan').filter(tag=member["tag"])
                clanId = 0
                if len(clan_qs) > 0:
                    clanId = clan_qs[0]['clan']

                exceededMembers.append({"name": member["name"], "tag": member["tag"], "clanId": clanId})

        return render(request, "clashdata/whoisout.html", {'missing_members': missingMembers, 'exceeded_members': exceededMembers, 
                                                                                'clans': clans, 'sel_clan_id': selectedClanId, 
                                                                                'total_line': line.count(), 'total_clan': len(currentMembers)})

from time import time
from django.http import JsonResponse

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

class CurrentWar(generic.View):

    def get(self, request):
        if is_ajax(request):
            clanTag = request.GET.get('tag_id')
            warInfo = clashapi.getCurrentWarInfo(clanTag)
            return JsonResponse({'warInfo': warInfo}, status=200)
        
        isColosseum = clashapi.isColosseum()
        clanTags = models.Clan.objects.exclude(tag__exact='')
        return render(request, "clashdata/currentwar.html", { 'clanTags': clanTags, 'isColosseum': isColosseum})

class CurrentWarAllies(generic.View):

    def get(self, request):
        if is_ajax(request):
            clanTag = request.GET.get('tag_id')
            warInfo = clashapi.getCurrentWarInfo(clanTag)
            return JsonResponse({'warInfo': warInfo}, status=200)
        
        isColosseum = clashapi.isColosseum()
        clanTags = models.ClanBR.objects.exclude(tag__exact='')
        return render(request, "clashdata/currentwarallies.html", { 'clanTags': clanTags, 'isColosseum': isColosseum})

class CurrentWarRival(LoginRequiredMixin, generic.View):

    def get(self, request):
        if is_ajax(request):
            clanTag = request.GET.get('tag_id')
            warInfo = clashapi.getCurrentWarInfo(clanTag)
            return JsonResponse({'warInfo': warInfo}, status=200)
        
        isColosseum = clashapi.isColosseum()
        clanTags = models.Rival.objects.exclude(tag__exact='')
        return render(request, "clashdata/currentwarrival.html", { 'clanTags': clanTags, 'isColosseum': isColosseum})

class MissingPlayers(generic.View):

    def get(self, request):
        if is_ajax(request):
            clanTag = request.GET.get('tag_id')
            line = models.ClanMember.objects.values('tag', 'name').filter(clan__tag=clanTag)
            missing = clashapi.whoIsMissing(clanTag, line)

            return JsonResponse({'missingInfo': missing}, status=200)
        
        clanTags = models.Clan.objects.exclude(tag__exact='')
        return render(request, "clashdata/missing_players.html", { 'clanTags': clanTags })

def getLines(request):
    line = models.ClanMember.objects.all().order_by("clan_id")
    clanInfo = {}

    #print(line)
    for i in line:
        clanName = i.clan.name
        tag = i.tag

        if clanName in clanInfo:
            clanInfo[clanName].append(tag)
        else:
            clanInfo[clanName] = [tag]

    return JsonResponse({'json': clanInfo}, status=200)

class Tournament(generic.View):
    
    def get(self, request):
        return render(request, "clashdata/tournament.html")

class Dima(generic.View):

    def get(self, request):
        if is_ajax(request):
            clanTag = request.GET.get('tag_id')
            warInfo = clashapi.getCurrentWarInfo(clanTag)
            missing = clashapi.whoIsMissing(clanTag, [])

            return JsonResponse({'warInfo': warInfo, 'missingInfo': missing}, status=200)
        
        isColosseum = clashapi.isColosseum()
        clanTags = ['#YU9GRGG']
        return render(request, "clashdata/dima.html", { 'clanTags': clanTags, 'isColosseum': isColosseum})

def getTrainingDays(request, tag):
    tag = "#" + tag
    currentSeason = clashapi.getCurrentSeason(tag)
    trainingInfo = {}

    trainingInfo["season"] = currentSeason
    trainingInfo["tag"] = tag
    trainingInfo["data"] = clashapi.getTrainingDays(tag)

    return JsonResponse({'json': trainingInfo}, status=200)

def getTrainingDaysBySeason(request, tag, season):

    trainingInfo = []

    try:
        tag = "#" + tag
        clan = models.Clan.objects.get(tag=tag)
        war = models.War.objects.get(clan_id=clan.id,identifier=season)
        trainingDays = models.TrainingDay.objects.filter(war_id=war.id)

        for i in trainingDays:
            trainingInfo.append(
                {
                    "Tag": i.tag,
                    "DecksUsed": i.decksUsed,
                    "DecksUsedToday": i.decksUsedToday,
                    "DecksTraining": i.decksTraining
                }
            )
    except Exception as error:
        trainingInfo = []

    return JsonResponse({'json': trainingInfo}, status=200)

class CreateClanBR(LoginRequiredMixin, generic.CreateView):
    form_class = forms.ClanBRCreateForm
    success_url = reverse_lazy('clashdata:clansBR')
    template_name = 'clashdata/clanbr_form.html'

class DeleteClanBR(LoginRequiredMixin, generic.DeleteView):
    model = models.ClanBR
    success_url = reverse_lazy("clashdata:clansBR")
        
class UpdateClanBR(LoginRequiredMixin, generic.UpdateView):
    model = models.ClanBR
    form_class = forms.ClanCreateForm
    success_url = reverse_lazy('clashdata:clansBR')
    template_name = 'clashdata/clanbr_form.html'

class ListClansBR(generic.ListView):
    model = models.ClanBR

class ClansWar(generic.ListView):
    model = models.ClanBR
    context_object_name = 'clans'
    template_name = 'clashdata/clanswar.html'

class ClanWar(generic.View):
    def get(self, request):
        if is_ajax(request):
            clanTag = request.GET.get('tag_id')
            warInfo = clashapi.getCurrentWarInfo(clanTag)
            missing = clashapi.whoIsMissing(clanTag, [])
            missed = clashapi.getWhoMissedCurrentWarForClanBrs(clanTag, missing["currentMembers"])
            return JsonResponse({'warInfo': warInfo, 'missingInfo': missing, 'missed': missed}, status=200)
        
        errorMsg = None
        bError = 0
        isColosseum = False

        try:
            tag = request.GET.get('clan')
            tag = "#" + tag
            isColosseum = clashapi.isColosseumNew(tag)
            name = clashapi.getClanData(tag)["name"]

            log = models.LogClansWar(tag=tag, name=name)
            log.save()

        except Exception as error:
            errorMsg = f"Não foi possível carregar clã com a TAG {tag}"
            bError = 1

        return render(request, "clashdata/clanwar.html", { 'clan': tag, 'isColosseum': isColosseum, 'error': errorMsg, 'hasError': bError})

class ListLogClansWar(LoginRequiredMixin, generic.ListView):
    model = models.LogClansWar
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return filters.LogClansWarFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = filters.LogClansWarFilter(self.request.GET, queryset=self.get_queryset())
        return context

def getLastSeason(request, clanTag):
    clanTag = "#" + clanTag
    lastSeason = clashapi.getLastSeason(clanTag)
    return JsonResponse({'json': lastSeason}, status=200)

def getPlayersWarInfo(request, clanTag, season):
    clanTag = "#" + clanTag
    playersWarInfo = clashapi.getPlayersWarInfo(clanTag, season)
    return JsonResponse({'json': playersWarInfo}, status=200)

def searchPlayersWarInfo(request):
    selectedClanId = request.GET.get('clan', None)
    selectedSeasons = request.GET.get('seasons', None)
    selectedOrderBy = request.GET.get('inlineOrderBy', None)
    additionalClans = request.GET.get('additionalClans', None)
    includeplayers = request.GET.get('includeplayers', None)
    source = request.GET.get('source', 'line')
    clans = models.Clan.objects.all().exclude(name="Aposentados").exclude(tag="")
    seasons = models.War.objects.all().order_by('-identifier').values('identifier').distinct()[:5]     

    if selectedClanId is None or selectedSeasons is None or selectedSeasons == "":
        currentSeason = clashapi.getCurrentSeason(clans.first().tag)
        if seasons.first()["identifier"] == currentSeason   :
            seasons = seasons[1:]
        return render(request, "clashdata/playerswarinfo_list.html", {'clans': clans, 'seasons': seasons, 'sel_clan_id': selectedClanId })
    
    selectedClanInfo = models.Clan.objects.filter(id=selectedClanId).first()

    bScore = False
    bIncludePlayers = False
    lstSeasons = selectedSeasons.split(',')
    lstAdditionalClans = []
    
    if not additionalClans == "" and not additionalClans is None:
        lstAdditionalClans = additionalClans.split(',')

    if not includeplayers is None:
        bIncludePlayers = True

    allPlayersInfo = [] 
    playersToBeAnalyed = []

    if source == "line":
        playersToBeAnalyed = models.ClanMember.objects.filter(clan_id=selectedClanId)
    else:    
        tagList = []
        for season in lstSeasons:
            war = models.War.objects.filter(identifier=season, clan_id=selectedClanId).first()
            playerInfoList = models.PlayersWarInfo.objects.filter(war=war)
            tagList.extend(x.tag for x in playerInfoList if x.tag not in tagList)
        
        for tagPlayer in tagList:
            info = models.ClanMember.objects.filter(tag=tagPlayer).first()
            if info is None:
                if source == "all":
                    playerData = clashapi.getPlayerInfo(tagPlayer)
                    if not playerData["name"] == "":
                        clanMember = models.ClanMember(
                            tag=tagPlayer,
                            name=playerData["name"] + "(not found)"
                        )
                        playersToBeAnalyed.append(clanMember)    
            else:
                playersToBeAnalyed.append(info)

    clanAvg = 0
    clanFame = 0

    for player in playersToBeAnalyed:
        totalFame = 0
        totalAtks = 0
        seasonsInfo = []

        for season in lstSeasons:
            war = models.War.objects.filter(identifier=season, clan_id=selectedClanId).first()
            playerInfo = models.PlayersWarInfo.objects.filter(war=war, tag=player.tag).first()

            otherClans = []
            atksSeason = 0
            fameSeason = 0
            avgSeason = 0

            if not playerInfo is None:
                atksSeason = playerInfo.atksWar
                fameSeason = playerInfo.fame

                clanFame = clanFame + fameSeason

            for additionalClanId in lstAdditionalClans: # get other clans infos
                if additionalClanId == selectedClanId:
                    continue

                additionalClan = models.Clan.objects.filter(id=additionalClanId).first()
                warOtherClan = models.War.objects.filter(identifier=season, clan_id=additionalClanId).first()
                playerInfoOtherClan = models.PlayersWarInfo.objects.filter(war=warOtherClan, tag=player.tag).first()

                if not playerInfoOtherClan is None:
                    atksSeason = atksSeason + playerInfoOtherClan.atksWar
                    fameSeason = fameSeason + playerInfoOtherClan.fame
                    otherClans.append(additionalClan.name)
            
            totalAtks = totalAtks + atksSeason
            totalFame = totalFame + fameSeason
            if fameSeason > 0:
                avgSeason = fameSeason / atksSeason

            seasonsInfo.append({
                "Name": season,
                "Atks": atksSeason,
                "Fame": fameSeason,
                "Average": avgSeason,
                "OtherClans": otherClans
            })

        avg = 0
        if totalFame > 0:
            avg = totalFame / totalAtks

        clanAvg = clanAvg + avg

        if not bIncludePlayers and totalFame == 0:
            continue

        allPlayersInfo.append({
            "Average": avg,
            "Name": player.name,
            "Tag": player.tag,
            "Atks": totalAtks,
            "Seasons": seasonsInfo
        })
    
    if selectedOrderBy == "fame":
        allPlayersInfo.sort(key=lambda x: [p["Fame"] for p in x["Seasons"]], reverse=True)
    elif selectedOrderBy == "atks":
        allPlayersInfo.sort(key=lambda x: x["Atks"], reverse=False)
    else:
        allPlayersInfo.sort(key=lambda x: x["Average"], reverse=True)

    if clanAvg > 0:
        clanAvg = clanAvg / len(allPlayersInfo)

    return render(request, "clashdata/playerswarinfo_list.html", {
        'clanName': selectedClanInfo.name,
        'clans': clans, 
        'sel_clan_id': selectedClanId, 
        'seasons': seasons,
        'lstAdditionalClans': lstAdditionalClans,
        'lstSeasons': lstSeasons,
        "result": allPlayersInfo,
        "orderby": selectedOrderBy,
        "includePlayers": bIncludePlayers,
        "source": source,
        "clanAverage": clanAvg,
        "clanFame": clanFame
    })

class CurrentWarMissed(generic.View):

    def get(self, request):
        if is_ajax(request):
            clanTag = request.GET.get('tag_id')
            missing = clashapi.getWhoMissedCurrentWar(clanTag)
            return JsonResponse({'missingInfo': missing}, status=200)
        
        clanTags = models.Clan.objects.exclude(tag__exact='')
        return render(request, "clashdata/missingcurrentwar.html", { 'clanTags': clanTags })