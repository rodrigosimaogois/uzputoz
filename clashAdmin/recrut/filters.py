from cgitb import lookup
import django_filters

from django_filters import DateFilter, CharFilter
from . import models

class CandidateFilter(django_filters.FilterSet):
    nickname = CharFilter(field_name="nickname", lookup_expr='icontains', label="Nome")
    tag = CharFilter(field_name="tag", lookup_expr='icontains', label="Tag")

    class Meta:
        model = models.Candidate
        fields = '__all__'
        exclude = ['email', 'whatsapp', 'level', 'datetime', 'clan']