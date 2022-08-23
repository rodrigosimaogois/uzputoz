import requests
import json
from . import models
from django.shortcuts import get_object_or_404

def __callEndPoint(url):
    token = get_object_or_404(models.Config, name="clashapi")

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token.value}'
    }

    response = requests.get(url,headers=headers)

    if response.status_code != 200:
        print(f"error: {response.status_code}: {response._content}")
        raise Exception(f"{response.status_code}: {response._content}")

    return response.json()

def getClanMembers(clanTag):
    tag = clanTag.tag.replace("#","")
    jsonResponse = __callEndPoint(f"https://api.clashroyale.com/v1/clans/%23{tag}/members")
    print(jsonResponse)
    currentMembers = jsonResponse["items"]
    return currentMembers
