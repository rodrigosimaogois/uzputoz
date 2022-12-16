from django.urls import path, include
from django.contrib.auth import views as auth_views

from .models import Clan
from . import views

app_name = 'clashdata'

urlpatterns = [
    path('', views.ListMembers.as_view(), name='members'),
    path("clanList/", views.ListClans.as_view(), name="clans"),
    path("newclan/", views.CreateClan.as_view(), name="createclan"),
    path("editclan/<pk>/",views.UpdateClan.as_view(),name="editclan"),
    path("deleteclan/<pk>/",views.DeleteClan.as_view(),name="deleteclan"),
    path("memberList/", views.ListMembers.as_view(), name="members"),
    path("newMember/", views.CreateClanMember.as_view(), name="createmember"),
    path("editMember/<pk>/",views.UpdateClanMember.as_view(),name="editmember"),
    path("deleteMember/<pk>/",views.DeleteClanMember.as_view(),name="deletemember"),
    path('memberList/changeClan/<pk>/<newclan>/<currentfilter>/', views.changeClan, name='changeclan'),
    path("history/", views.ListClanHistory.as_view(), name="clanHistory"),
    path("whoisout/", views.missingMembers, name="whoisout"),
    path("currentwar/", views.CurrentWar.as_view(), name="currentwar"),
    path("getLines/", views.getLines, name="getLines"),
    path("currentwarrival/", views.CurrentWarRival.as_view(), name="currentwarrival"),
    path("missingplayers/", views.MissingPlayers.as_view(), name="missingplayers"),
    path("tournament/", views.Tournament.as_view(), name="tournament"),
    path("dima/", views.Dima.as_view(), name="dima"),
    path("getTrainingDays/<tag>", views.getTrainingDays, name="getTrainingDays"),
]