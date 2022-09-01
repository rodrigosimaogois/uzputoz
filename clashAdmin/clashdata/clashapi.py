import requests
import json
from . import models
from django.shortcuts import get_object_or_404

def __callEndPoint(url):
    token = get_object_or_404(models.Config, name="clashapi")

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token.value}'
    }

    response = requests.get(url,headers=headers)

    if response.status_code != 200:
        print(f"error: {response.status_code}: {response._content}")
        raise Exception(f"{response.status_code}: {response._content}")

    return response.json()

def getClanMembers(clanTag):
    tag = clanTag.tag.replace("#","")
    jsonResponse = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/members")
    print(jsonResponse)
    currentMembers = jsonResponse["items"]
    return currentMembers

def __getClanInfo(clanData, maxAttacks, isColosseum):
        usedDecksCount = 0
        usedDecksTodayCount = 0
        peopleTodayCount = 0
        totalFame = 0
        periodPoints = clanData["periodPoints"]
        maxPossiblePointsPlayersMissingAttacks = 0

        for participant in clanData["participants"]:
            usedDecksCount += participant["decksUsed"]
            totalFame += participant["fame"]
            if(participant["decksUsedToday"] > 0):
                peopleTodayCount+=1
                usedDecksTodayCount += participant["decksUsedToday"]
                faltantes = 4 - participant["decksUsedToday"]

                if faltantes > 0 and faltantes < 4:
                    if faltantes == 3:
                        maxPossiblePointsPlayersMissingAttacks += 700
                    else:
                        maxPossiblePointsPlayersMissingAttacks += (200 * faltantes)
 
        totalUsedDecksWithoutTrainingDecks = 0
        totalUsedDecksWithoutTrainingDecks = maxAttacks + usedDecksTodayCount

        if isColosseum:
            periodPoints = totalFame

        if not periodPoints == 0:
            if totalUsedDecksWithoutTrainingDecks == 0:
                average = periodPoints
            else:
                average = periodPoints/totalUsedDecksWithoutTrainingDecks
        else:
            average = 0

        missingDecksToday = 200 - usedDecksTodayCount

        pessoasFaltando = 50 - peopleTodayCount
        maxPossiblePoints = (pessoasFaltando * 900) + maxPossiblePointsPlayersMissingAttacks + periodPoints
        minPossiblePoints = (missingDecksToday * 100) + periodPoints

        clanInfo = { 
                "Tag": clanData["tag"], 
                "Name": clanData["name"],
                "Fame": clanData["fame"],
                "Total": periodPoints,
                "TotalDecks": totalUsedDecksWithoutTrainingDecks,
                "DecksToday": usedDecksTodayCount,
                "PlayersToday": peopleTodayCount,
                "MissingAttacksToday": missingDecksToday,
                "Average": "{:.2f}".format(average),
                "MinPoints": minPossiblePoints,
                "MaxPoints": maxPossiblePoints,
                "Estimation": periodPoints + (missingDecksToday * int(average))
            }
        
        return clanInfo


def getCurrentWarInfo(clanTag):
        tag = clanTag.replace("#","")
        clansInfos = []
        
        currentRiverRace = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/currentriverrace")

        isColosseum = currentRiverRace["periodType"] == "colosseum"
        periodIndex = currentRiverRace["periodIndex"]
        
        weekDay = periodIndex % 7
        maxAttacks = 200 * (weekDay - 3) # 3 == first war day

        if not isColosseum:
            maxAttacks = 0

        for clan in currentRiverRace["clans"]:
            clanInfo = __getClanInfo(clan, maxAttacks, isColosseum)
            clansInfos.append(clanInfo)
        
        clansInfos.sort(key=lambda x: x["Total"], reverse=True)

        warInfo = {
            "colosseum": isColosseum,
            "clansInfos":  clansInfos
        }

        return warInfo

def isColosseum():
    currentRiverRace = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%2320RGVR8/currentriverrace")
    isColosseum = currentRiverRace["periodType"] == "colosseum"
    return isColosseum
