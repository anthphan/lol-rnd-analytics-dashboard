import csv
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from core.models import (
    Team,
    Player,
    Match,
    PlayerMatchStats,
    TeamMatchSummary,
)


def _to_int(value: str):
    if value is None:
        return None
    v = value.strip()
    if v == "":
        return None
    return int(v)


def _to_float(value: str):
    if value is None:
        return None
    v = value.strip()
    if v == "":
        return None
    return float(v)


def _parse_dt(value: str):
    if not value:
        raise CommandError("played_at is required in match.csv")

    dt = parse_datetime(value.strip())
    if dt is None:
        raise CommandError(
            f"Could not parse played_at datetime: '{value}'. "
            "Use ISO format like 2026-02-12T19:00:00-05:00"
        )

    # If datetime is naive, assume local timezone
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())

    return dt


class Command(BaseCommand):
    help = "Import PMT-style match + team summary + player stats from CSV files."

    def add_arguments(self, parser):
        parser.add_argument("match_csv", type=str, help="Path to match.csv")
        parser.add_argument("pmt_csv", type=str, help="Path to pmt_game.csv")

    def handle(self, *args, **options):
        match_csv_path = options["match_csv"]
        pmt_csv_path = options["pmt_csv"]

        # 1) Load match metadata (match.csv) into dict by external_id
        matches_by_id = {}
        with open(match_csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {"match_external_id", "patch",
                        "played_at", "duration_minutes"}
            if not required.issubset(set(reader.fieldnames or [])):
                raise CommandError(
                    f"match.csv must include headers: {', '.join(sorted(required))}"
                )

            for row in reader:
                ext_id = row["match_external_id"].strip()
                matches_by_id[ext_id] = {
                    "patch": row["patch"].strip(),
                    "played_at": _parse_dt(row["played_at"]),
                    "duration_minutes": _to_int(row["duration_minutes"]),
                }

        if not matches_by_id:
            raise CommandError("match.csv had no rows.")

        # 2) Read PMT rows and import
        created_matches = 0
        created_team_summaries = 0
        created_players = 0
        created_player_stats = 0

        with open(pmt_csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {
                "match_external_id",
                "row_type",
                "team",
                "side",
                "player_name",
                "role",
                "champion",
                "kills",
                "deaths",
                "assists",
                "cs",
                "gold",
                "bans_1",
                "bans_2",
                "bans_3",
                "bans_4",
                "bans_5",
                "gold_k",
                "team_kills",
                "towers",
                "objectives_shorthand",
            }
            if not required.issubset(set(reader.fieldnames or [])):
                raise CommandError(
                    f"pmt_game.csv must include headers: {', '.join(sorted(required))}"
                )

            for row in reader:
                ext_id = row["match_external_id"].strip()

                if ext_id not in matches_by_id:
                    raise CommandError(
                        f"Match external_id '{ext_id}' appears in pmt_game.csv "
                        f"but not in match.csv"
                    )

                # Upsert match
                match_defaults = matches_by_id[ext_id]
                match, match_created = Match.objects.update_or_create(
                    external_id=ext_id,
                    defaults={
                        "patch": match_defaults["patch"],
                        "played_at": match_defaults["played_at"],
                        "duration_minutes": match_defaults["duration_minutes"],
                    },
                )
                if match_created:
                    created_matches += 1

                row_type = row["row_type"].strip().lower()
                team_name = row["team"].strip()
                side = row["side"].strip().lower()

                # Ensure team exists (region unknown from PMT, use blank/NA for now)
                team, _ = Team.objects.get_or_create(
                    name=team_name,
                    defaults={"region": "NA"},
                )

                if row_type == "team":
                    # Upsert TeamMatchSummary
                    summary, created = TeamMatchSummary.objects.update_or_create(
                        match=match,
                        team=team,
                        defaults={
                            "side": side,
                            "bans_1": (row["bans_1"] or "").strip(),
                            "bans_2": (row["bans_2"] or "").strip(),
                            "bans_3": (row["bans_3"] or "").strip(),
                            "bans_4": (row["bans_4"] or "").strip(),
                            "bans_5": (row["bans_5"] or "").strip(),
                            "gold_k": _to_float(row["gold_k"]),
                            "team_kills": _to_int(row["team_kills"]),
                            "towers": _to_int(row["towers"]),
                            "objectives_shorthand": (row["objectives_shorthand"] or "").strip(),
                        },
                    )
                    if created:
                        created_team_summaries += 1

                elif row_type == "player":
                    player_name = row["player_name"].strip()
                    role = row["role"].strip()

                    player, created = Player.objects.get_or_create(
                        summoner_name=player_name,
                        defaults={"team": team, "role": role},
                    )
                    # If player exists but team/role changed, update it
                    changed = False
                    if player.team_id != team.id:
                        player.team = team
                        changed = True
                    if player.role != role:
                        player.role = role
                        changed = True
                    if changed:
                        player.save()

                    if created:
                        created_players += 1

                    # Create / update PlayerMatchStats
                    champion = row["champion"].strip()
                    kills = _to_int(row["kills"])
                    deaths = _to_int(row["deaths"])
                    assists = _to_int(row["assists"])
                    cs = _to_int(row["cs"])
                    gold = _to_int(row["gold"])


                    if kills is None or deaths is None or assists is None:
                        raise CommandError(
                            f"Missing K/D/A for player row: {player_name} in match {ext_id}"
                        )

                    pms, created = PlayerMatchStats.objects.update_or_create(
                        match=match,
                        player=player,
                        defaults={
                            "champion": champion,
                            "kills": kills,
                            "deaths": deaths,
                            "assists": assists,
                            "cs": cs,
                            "gold": gold,
                        },
                    )
                    if created:
                        created_player_stats += 1

                else:
                    raise CommandError(
                        f"Unknown row_type '{row_type}'. Use 'team' or 'player'."
                    )

        self.stdout.write(self.style.SUCCESS("Import completed!"))
        self.stdout.write(
            f"Matches created: {created_matches}\n"
            f"Team summaries created: {created_team_summaries}\n"
            f"Players created: {created_players}\n"
            f"PlayerMatchStats created: {created_player_stats}"
        )
