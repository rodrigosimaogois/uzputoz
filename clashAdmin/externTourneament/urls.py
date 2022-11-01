from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'externTourneament'

urlpatterns = [
    path('', views.RegisterParticipantView.as_view(), name='register'),
    #path('confirm/<token>/', views.confirm, name='confirmRegistration'),
    #path('email/<to>/', views.email, name='email'),
]