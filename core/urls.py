from django.urls import path
from .views import player_overview

urlpatterns = [
    path("players/", player_overview),
]
