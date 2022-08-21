from django.contrib import admin
from .models import Clan, ClanMember, ClanMemberHistory

# Register your models here.

admin.site.register(Clan)
admin.site.register(ClanMember)
admin.site.register(ClanMemberHistory)