import requests
import json
from . import models
from django.shortcuts import get_object_or_404
from datetime import datetime
from dateutil import tz

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Sao_Paulo')

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
    currentMembers = jsonResponse["items"]
    return currentMembers

def __getClanInfo(clanData, maxAttacks, isColosseum, boatInfo):
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

        boat = boatInfo[clanData["tag"]]
        defenses = 0
        boatPoints = 0

        if not isColosseum:
            defenses = boat["Defenses"]
            boatPoints = boat["BoatPoints"]

        clanInfo = { 
                "Tag": clanData["tag"], 
                "Name": clanData["name"],
                "ClanScore": clanData["clanScore"],
                "Fame": clanData["fame"],
                "Total": periodPoints,
                "TotalDecks": totalUsedDecksWithoutTrainingDecks,
                "DecksToday": usedDecksTodayCount,
                "PlayersToday": peopleTodayCount,
                "MissingAttacksToday": missingDecksToday,
                "Average": "{:.2f}".format(average),
                "MinPoints": minPossiblePoints,
                "MaxPoints": maxPossiblePoints,
                "Estimation": periodPoints + (missingDecksToday * int(average)),
                "Defenses": defenses,
                "BoatPoints": boatPoints
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

        boatInfo = dict()
        boatPrize = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]

        if(currentRiverRace["periodType"] == "warDay"):
            periods = currentRiverRace["periodLogs"][-1:]
            for period in periods:                
                for item in period["items"]:
                    tag = item["clan"]["tag"]
                    defenses = item["numOfDefensesRemaining"]
                    
                    totalBoatPoints = 0
                    for i in range(defenses):
                        totalBoatPoints += boatPrize[i]

                    boatInfo[tag] = {
                        "Defenses": defenses,
                        "BoatPoints": totalBoatPoints
                    }

        for clan in currentRiverRace["clans"]:
            clanInfo = __getClanInfo(clan, maxAttacks, isColosseum, boatInfo)
            clansInfos.append(clanInfo)
        
        clansInfos.sort(key=lambda x: x["Total"], reverse=True)

        warInfo = {
            "clanName": currentRiverRace["clan"]["name"],
            "colosseum": isColosseum,
            "clansInfos":  clansInfos
        }

        return warInfo

def isColosseum():
    currentRiverRace = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%2320RGVR8/currentriverrace")
    isColosseum = currentRiverRace["periodType"] == "colosseum"
    return isColosseum

def whoIsMissing(clanTag, currentLine):
    tag = clanTag.replace("#","")

    currentMembers = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/members")
    currentRiverRace = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/currentriverrace")

    isColosseum = currentRiverRace["periodType"] == "colosseum"

    if currentRiverRace["clan"]["fame"] > 10000 and not isColosseum:
        return {
            "clanName": currentRiverRace["clan"]["name"],
            "totalDecks": 200,
            "totalMissing": 0,
            "totalMissingParticipants": 0,
            "missingPlayers": []
        }

    totalUsedDecks = 0
    totalParticipants = 0

    allConsideredPlayers = []

    for participant in currentRiverRace["clan"]["participants"]:
        totalUsedDecks += participant["decksUsedToday"]
        if participant["decksUsedToday"] > 0:
            totalParticipants = totalParticipants + 1

    totalMissingParticipants = 50 - totalParticipants

    decksMissingParticipants = totalMissingParticipants * 4
    totalMissingDecks = 200 - decksMissingParticipants - totalUsedDecks

    missingPlayers = []

    for participant in currentRiverRace["clan"]["participants"]:
        decksUsedToday = participant["decksUsedToday"]

        if decksUsedToday == 4:
            allConsideredPlayers.append(participant["tag"])
            continue

        found = [x for x in currentMembers["items"] if x["tag"] == participant["tag"]]

        if len(found) > 0:
            try:
                lastSeen = found[0]["lastSeen"]
                dt_obj = datetime.strptime(lastSeen, '%Y%m%dT%H%M%S.%fZ')

                utc = dt_obj.replace(tzinfo=from_zone)
                local = utc.astimezone(to_zone)

                allConsideredPlayers.append(participant["tag"])
                missingPlayers.append({
                    "name": participant["name"],
                    "missingDecks": 4 - participant["decksUsedToday"],
                    "lastSeen": local.strftime("%d-%m-%Y %H:%M:%S"),
                    "inClan": True
                })
            except Exception as error:
                allConsideredPlayers.append(participant["tag"])
                missingPlayers.append({
                    "name": participant["name"],
                    "missingDecks": 4 - participant["decksUsedToday"],
                    "lastSeen": {},
                    "inClan": True
                })
        else:
            if decksUsedToday > 0:
                allConsideredPlayers.append(participant["tag"])
                missingPlayers.append({
                    "name": participant["name"],
                    "missingDecks": 4 - participant["decksUsedToday"],
                    "lastSeen": {},
                    "inClan": False
                })

    for expectedMember in currentLine:
        if not expectedMember["tag"] in allConsideredPlayers:
            missingPlayers.append({
                "name": expectedMember["name"],
                "missingDecks": 4,
                "lastSeen": {},
                "inClan": False
            })
                
    missingPlayers.sort(key=lambda x: x["missingDecks"], reverse=False)

    clanInfo = {
        "clanName": currentRiverRace["clan"]["name"],
        "totalDecks": totalUsedDecks,
        "totalMissing": totalMissingDecks,
        "totalMissingParticipants": totalMissingParticipants,
        "missingPlayers": missingPlayers
    }

    return clanInfo

def getPlayerInfo(playerTag):
    try:
        tag = playerTag.replace("#","")
        playerInfo = __callEndPoint(f"https://api.clashroyale.com/v1/players/%23{tag}")
        return playerInfo
    except Exception as error:
        return {
            "name": "",
            "clan": { 
                "name": "" 
            }
        }

def getCurrentSeason(clanTag):
    tag = clanTag.replace("#","")

    currentRiverRace = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/currentriverrace")
    riverraceLog = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/riverracelog")

    seasonId = riverraceLog["items"][0]["seasonId"]
    index = riverraceLog["items"][0]["sectionIndex"]
    if currentRiverRace["sectionIndex"] == 0:
        index = 0
        seasonId += 1
    else:
        index +=1

    return f"{seasonId}-{index}"

def getTrainingDays(clanTag):
    tag = clanTag.replace("#","")
    currentRiverRace = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/currentriverrace")

    periodIndex = currentRiverRace["periodIndex"]
    if not periodIndex % 7 == 3:
        return

    trainingInfo = []

    for participant in currentRiverRace["clan"]["participants"]:
        participantInfo = {
            "Name": participant["name"],
            "Tag": participant["tag"],
            "DecksUsed": participant["decksUsed"],
            "DecksUsedToday": participant["decksUsedToday"],
            "DecksTraining": participant["decksUsed"] - participant["decksUsedToday"] 
        }
        
        trainingInfo.append(participantInfo)

    return trainingInfo
