from django.contrib import admin
from .models import Clan, ClanMember

# Register your models here.

admin.site.register(Clan)
admin.site.register(ClanMember)