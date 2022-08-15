from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from datetime import datetime
# Create your models here.

from django.contrib.auth import get_user_model
User = get_user_model()

class Clan(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        super().save(args, kwargs)

    def get_absolute_url(self):
        return reverse("clans")

    class Meta:
        ordering = ["name"]   

class ClanMember(models.Model):
    clan = models.ForeignKey(Clan, related_name='clan_memberships', on_delete=models.CASCADE)
    
    tag = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    cargo = models.IntegerField(default=0)
    media = models.FloatField(default=0.0)
    creation_time = models.TimeField(auto_now=True)
    contato = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.tag})"

    def save(self, *args, **kwargs):
        super().save(args, kwargs)

    def get_absolute_url(self):
        return reverse("members")
    
    class Meta:
        ordering = ["clan", "name"]

    def changeClan(self, newClan):
        self.clan = newClan
        self.save()
    
    


