from clashdata import clashapi
from clashdata import models

def run():
    x = models.Clan.objects.all()
    print(x)
    

