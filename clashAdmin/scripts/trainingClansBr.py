from clashdata import clashapi
from clashdata import models

import requests

def getTrainingDays(tag):
    response = requests.get(f"https://www.uzputoz.com.br/clashdata/getTrainingDays/{tag}")
    if response.status_code != 200:
        print(f"error: {response.status_code}: {response._content}")
    return response.json()

def run():
    clansBrs = models.ClanBR.objects.all()

    for i in range(len(clansBrs)):
        tag = clansBrs[i].tag.replace("#","")
        print(clanInfoi)
        
        try:
            clanInfoi = getTrainingDays(tag)["json"]

            if clanInfoi["data"] is None:
                print("still training day")
            else:
                clanBr = models.ClanBR.objects.get(tag=clanInfoi["tag"])
                warBr, created = models.WarClans.objects.get_or_create(identifier=clanInfoi["season"], clan=clanBr)
                warBr.save()

                for training in clanInfoi["data"]:
                    playerTag = training["Tag"]
                    decksUsed = training["DecksUsed"]
                    decksUsedToday = training["DecksUsedToday"]
                    decksTraining = training["DecksTraining"]

                    trainingBr = models.TrainingDayClans(
                        tag = playerTag,
                        decksUsed = decksUsed,
                        decksUsedToday = decksUsedToday,
                        decksTraining = decksTraining,
                        war = warBr
                    )

                    trainingBr.save()
        except:
            print("error getting training day")