from cgitb import lookup
import django_filters

from django_filters import DateFilter, CharFilter
from . import models

class ClanMemberFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr='icontains', label="Nome")
    tag = CharFilter(field_name="tag", lookup_expr='icontains', label="Tag")

    class Meta:
        model = models.ClanMember
        fields = '__all__'
        exclude = ['cargo', 'media', 'creation_time', 'contato']

class ClanHistoryFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr='icontains', label="Nome")
    tag = CharFilter(field_name="tag", lookup_expr='icontains', label="Tag")
    #start_date = DateFilter(field_name="date", lookup_expr='gte', label="Data inicial")
    #end_date = DateFilter(field_name="date", lookup_expr='lte', label="Data final")

    class Meta:
        model = models.ClanMemberHistory
        fields = '__all__'
        exclude = ['date', 'clanSource', 'clanDestiny']