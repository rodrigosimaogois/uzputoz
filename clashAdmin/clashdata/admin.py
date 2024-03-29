from django.contrib import admin
from .models import Clan, ClanMember, ClanMemberHistory, Config, Rival, War, TrainingDay, ClanBR, LogClansWar, WarClans, TrainingDayClans

# Register your models here.

admin.site.register(Clan)
admin.site.register(ClanMember)
admin.site.register(ClanMemberHistory)
admin.site.register(Config)
admin.site.register(Rival)
admin.site.register(War)
admin.site.register(TrainingDay)
admin.site.register(ClanBR)
admin.site.register(LogClansWar)
admin.site.register(WarClans)
admin.site.register(TrainingDayClans)