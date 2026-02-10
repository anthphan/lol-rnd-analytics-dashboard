from django.shortcuts import render
from .models import Player, PlayerMatchStats
from django.db.models import Avg


def player_overview(request):
    players = Player.objects.all()

    data = []
    for player in players:
        avg_gold = PlayerMatchStats.objects.filter(
            player=player
        ).aggregate(Avg("gold"))["gold__avg"]

        data.append({
            "player": player,
            "avg_gold": avg_gold,
        })

        return render(request, "player_overview.html", {
            "data": data
        })
# Create your views here.
