from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'recrut'

urlpatterns = [
    path('', views.RegisterCandidateView.as_view(), name='register'),
    path("candidateList/", views.ListCandidates.as_view(), name="candidates"),
    path("deletecandidate/<pk>/",views.DeleteCandidate.as_view(),name="deletecandidate"),
]