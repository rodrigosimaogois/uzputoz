from email.policy import default
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from datetime import datetime
# Create your models here.

class RegisteredPlayers(models.Model):
    name = models.CharField(max_length=255, default="")
    nickname = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    clan = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255)
    whatsapp = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now=True)
    confirmed = models.BooleanField(default=False)
    wantInfo = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.nickname

    def save(self, *args, **kwargs):
        super().save(args, kwargs)

    class Meta:
        ordering = ["nickname"]   