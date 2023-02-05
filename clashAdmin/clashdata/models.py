from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from datetime import datetime
from model_utils import FieldTracker
# Create your models here.

from django.contrib.auth import get_user_model
User = get_user_model()

class Clan(models.Model):
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255, blank=True)

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

    name = models.CharField(max_length=255)    
    tag = models.CharField(max_length=255, unique=True)
    cargo = models.IntegerField(default=0)
    media = models.FloatField(default=0.0)
    creation_time = models.DateTimeField(auto_now=True)
    contato = models.CharField(max_length=255, blank=True)

    tracker = FieldTracker()

    def __str__(self) -> str:
        return f"{self.name} ({self.tag})"

    def save(self, *args, **kwargs):
        changedClan = self.tracker.has_changed('clan_id')
        super().save(args, kwargs)

        oldClan = kwargs.get('oldClan', '')

        if changedClan:
            history = ClanMemberHistory()
            history.add(self.name, self.tag, oldClan, self.clan.name)
 
    def delete(self, *args, **kwargs):
        super().delete(args, kwargs)
        history = ClanMemberHistory()
        history.add(self.name, self.tag, self.clan.name, '')
      
    def get_absolute_url(self):
        return reverse("members")
    
    class Meta:
        ordering = ["clan", "-media"]

    def changeClan(self, newClan):
        previousClan = self.clan
        self.clan = newClan
        self.save(oldClan=previousClan)        

class ClanMemberHistory(models.Model):    

    class Meta:
        ordering = ["-date"]

    name = models.CharField(max_length=255, blank=True)
    tag = models.CharField(max_length=255, blank=True)
    clanSource = models.CharField(max_length=255, blank=True)
    clanDestiny = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    def add(self, name, tag, oldClanName, newClanName):
        self.name = name
        self.tag = tag
        self.clanSource = oldClanName
        self.clanDestiny = newClanName
        self.save()

class Config(models.Model):
    name = models.CharField(max_length=255)
    value = models.TextField()

    def __str__(self) -> str:
        return self.name  

class Rival(models.Model):
    tag = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.tag

class War(models.Model):
    identifier = models.CharField(max_length=255)
    clan = models.ForeignKey(Clan, related_name='war_clan', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.identifier

class TrainingDay(models.Model):
    war = models.ForeignKey(War, related_name='trainingday_war', on_delete=models.CASCADE)
    tag = models.CharField(max_length=255, blank=True)
    decksUsed = models.IntegerField(default=0)        
    decksUsedToday = models.IntegerField(default=0)
    decksTraining = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.tag

class ClanBR(models.Model):
    tag = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.tag

class LogClansWar(models.Model):

    class Meta:
        ordering = ["-date"]

    tag = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name