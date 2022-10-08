from django.contrib import admin
from .models import Clan, ClanMember, ClanMemberHistory, Config, Rival

# Register your models here.

admin.site.register(Clan)
admin.site.register(ClanMember)
admin.site.register(ClanMemberHistory)
admin.site.register(Config)
admin.site.register(Rival)