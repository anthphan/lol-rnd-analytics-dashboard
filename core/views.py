from django.shortcuts import render
from .models import Player, PlayerMatchStats, Match, ObjectiveEvent, Vod, TeamMatchSummary
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

    from collections import defaultdict

    roles_order = ["TOP", "JNG", "MID", "BOT", "SUP"]

    team_players = defaultdict(dict)

    for s in stats:
        role = s.player.role.upper()
        team_name = s.player.team.name
        team_players[team_name][role] = s

    team_totals = {}

    for team_name, role_map in team_players.items():
        kills = sum(p.kills for p in role_map.values())
        deaths = sum(p.deaths for p in role_map.values())
        assists = sum(p.assists for p in role_map.values())

        team_totals[team_name] = f"{kills}-{deaths}-{assists}"

    teams = list(team_players.keys())
    if len(teams) == 2:
        team_left = teams[0]
        team_right = teams[1]
    else:
        team_left = team_right = None

    paired_rows = []

    if team_left and team_right:
        for role in roles_order:
            left = team_players[team_left].get(role)
            right = team_players[team_right].get(role)

            paired_rows.append({
                "role": role,
                "left": left,
                "right": right,
            })

    objectives = ObjectiveEvent.objects.filter(match=match).order_by("minute")
    vod = Vod.objects.filter(match=match).first()
    team_summaries = TeamMatchSummary.objects.filter(match=match)

    objective_rows = []
    for obj in objectives:
        computed = None
        if vod:
            computed = vod.game_start_offset_seconds + (obj.minute * 60)

        jump_seconds = obj.timestamp_seconds if obj.timestamp_seconds else computed

        objective_rows.append({
            "obj": obj,
            "jump_seconds": jump_seconds,
        })
    return render(request, "match_detail.html", {
        "match": match,
        "stats": stats,
        "vod": vod,
        "objective_rows": objective_rows,
        "team_summaries": team_summaries,
        "paired_rows": paired_rows,
        "team_totals": team_totals,
        "team_left": team_left,
        "team_right": team_right,
    })
