from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from datetime import datetime
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
    
    tag = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    cargo = models.IntegerField(default=0)
    media = models.FloatField(default=0.0)
    creation_time = models.DateTimeField(auto_now=True)
    contato = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.tag})"

    def save(self, *args, **kwargs):
        super().save(args, kwargs)
        history = ClanMemberHistory()
        history.add(self, kwargs.get('oldClan', None))
 
    # def delete(self, *args, **kwargs):

    #     #print(self.name)
    #     #print(self.clan)

    #     super().delete(args, kwargs)
        #history = ClanMemberHistory()
        #history.add(self, kwargs.get('oldClan', self.clan))
      
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

    clanMember = models.ForeignKey(ClanMember, related_name='member_histories', on_delete=models.CASCADE)
    operation = models.IntegerField(default=0) # 0 add, 1 change, 2 remove
    clanSource = models.ForeignKey(Clan, related_name='member_clan_source', on_delete=models.CASCADE, null=True)
    clanDestiny = models.ForeignKey(Clan, related_name='member_clan_destiny', on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now=True)

    def add(self, ClanMember, OldClan):
        self.clanMember = ClanMember
        self.clanSource = OldClan
        self.clanDestiny = ClanMember.clan
        self.save()

class RoyaleApiConfig(models.Model):
    ip = models.CharField(max_length=255)
    key = models.TextField()
    


