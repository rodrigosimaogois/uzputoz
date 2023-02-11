from clashdata import clashapi
from clashdata import models

import requests

def getLastSeason(tag):
    response = requests.get(f"https://www.uzputoz.com.br/clashdata/getLastSeason/{tag}")
    if response.status_code != 200:
        print(f"error: {response.status_code}: {response._content}")
    return response.json()

def getPlayersWarInfo(tag, season):
    response = requests.get(f"https://www.uzputoz.com.br/clashdata/getPlayersWarInfo/{tag}/{season}")
    if response.status_code != 200:
        print(f"error: {response.status_code}: {response._content}")
    return response.json()

def run():
    ourClanTags = ["20RGVR8", "9PGQJCRR", "YPU0GJUV", "PULQCRCP", "YYQGVLV9"]

    lastSeason = getLastSeason(ourClanTags[0])
    
    for ourClanTag in ourClanTags:
        clanTag = f"#{ourClanTag}"
        
        clan = models.Clan.objects.get(tag=clanTag)
        war, created = models.War.objects.get_or_create(identifier=lastSeason["json"], clan=clan)
        war.save() 

        isDataAlreadyInserted = models.PlayersWarInfo.objects.filter(war=war).exists()

        if isDataAlreadyInserted:
            print("playerWarInfo already exists")
            continue

        info = getPlayersWarInfo(ourClanTag, lastSeason["json"])["json"]
        isFinishedBefore = info["finishedBefore"]

        maxAttacks = 16

        if isFinishedBefore:
            maxAttacks = 12

        for playerInfo in info["playersInfo"]:
            playerTag = playerInfo["Tag"]
            atksTotal = playerInfo["Attacks"]
            fame = playerInfo["Fame"]
            boat = playerInfo["Boat"]
            atksTraining = 0
            atksWar = 0

            training = models.TrainingDay.objects.filter(war=war, tag=playerTag).first()
            
            if not training is None:
                atksTraining = training.decksTraining

            atksWar = atksTotal - atksTraining

            if atksWar > maxAttacks:
                atksWar = maxAttacks

            playerWarInfo = models.PlayersWarInfo(
                war = war,
                tag = playerTag,
                fame = fame,
                boats = boat,
                atksTotal = atksTotal,  
                atksTraining = atksTraining,
                atksWar = atksWar
            )

            playerWarInfo.save()