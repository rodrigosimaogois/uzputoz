from clashdata import clashapi
from clashdata import models

def run():
    clanset = models.Clan.objects.all()
    print(clanset)

    with open('readme.txt', 'w') as f:
        for clan in clanset:
            f.write(f"{clan.name}\r\n")
    

