from django.urls import path
from .views import player_overview, match_list, match_detail

urlpatterns = [
    path("players/", player_overview),
    path("matches/", match_list),
    path("matches/<int:match_id>/", match_detail),
]
