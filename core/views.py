from django.shortcuts import render
from .models import Player, PlayerMatchStats, Match, ObjectiveEvent, Vod
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


def match_list(request):
    matches = Match.objects.all().order_by("-played_at")

    return render(request, "match_list.html", {
        "matches": matches
    })


def match_detail(request, match_id):
    match = Match.objects.get(id=match_id)

    stats = PlayerMatchStats.objects.filter(match=match)
    objectives = ObjectiveEvent.objects.filter(match=match).order_by("minute")
    vod = Vod.objects.filter(match=match).first()

    return render(request, "match_detail.html", {
        "match": match,
        "stats": stats,
        "objectives": objectives,
        "vod": vod,
    })
