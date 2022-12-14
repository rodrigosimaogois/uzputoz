from clashdata import clashapi
from clashdata import models

def run():
    ourClanTags = ["#20RGVR8", "#9PGQJCRR", "#YPU0GJUV", "#PULQCRCP", "#YYQGVLV9"]

    currentSeason = clashapi.getCurrentSeason("#20RGVR8")
    print(currentSeason)

    for i in range(len(ourClanTags)):
        clanInfoi = clashapi.getTrainingDays(ourClanTags[i])

        if clanInfoi is None:
            print("still training day")
        else:
            
            clan = models.Clan.objects.get(tag=ourClanTags[i])
            war, created = models.War.objects.get_or_create(identifier=currentSeason, clan=clan)
            war.save()

            for training in clanInfoi:
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