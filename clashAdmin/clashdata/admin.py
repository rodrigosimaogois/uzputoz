from django.contrib import admin
from .models import Clan, ClanMember, ClanMemberHistory, Config

# Register your models here.

admin.site.register(Clan)
admin.site.register(ClanMember)
admin.site.register(ClanMemberHistory)
admin.site.register(Config)