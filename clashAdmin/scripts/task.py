from clashdata import clashapi
from clashdata import models

import requests

def getTrainingDays(tag):
    response = requests.get(f"https://www.uzputoz.com.br/clashdata/getTrainingDays/{tag}")
    if response.status_code != 200:
        print(f"error: {response.status_code}: {response._content}")
    return response.json()

def run():
    
    ourClanTags = []
    for clan in models.Clan.objects.all():
        if clan.tag != "" and clan.tag != "#Q208V9R2":
            ourClanTags.append(clan.tag.removeprefix("#"))

    for i in range(len(ourClanTags)):

        clanInfoi = getTrainingDays(ourClanTags[i])["json"]
        print(clanInfoi)

        if clanInfoi["data"] is None:
            print("still training day")
        else:
            clan = models.Clan.objects.get(tag=clanInfoi["tag"])
            war, created = models.War.objects.get_or_create(identifier=clanInfoi["season"], clan=clan)
            war.save()

            for training in clanInfoi["data"]:
                playerTag = training["Tag"]
                decksUsed = training["DecksUsed"]
                decksUsedToday = training["DecksUsedToday"]
                decksTraining = training["DecksTraining"]

                training = models.TrainingDay(
                    tag = playerTag,
                    decksUsed = decksUsed,
                    decksUsedToday = decksUsedToday,
                    decksTraining = decksTraining,
                    war = war
                )

                training.save()