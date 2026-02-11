from django.db import models

# Create your models here.


class Team(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    summoner_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.summoner_name


class Match(models.Model):
    patch = models.CharField(max_length=20)
    played_at = models.DateTimeField()

    def __str__(self):
        return f"Patch {self.patch} @ {self.played_at}"


class PlayerMatchStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    champion = models.CharField(max_length=50)

    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()

    cs = models.IntegerField()
    gold = models.IntegerField()

    def __str__(self):
        return f"{self.player} in match {self.match}"


class ObjectiveEvent(models.Model):
    OBJECTIVE_CHOICES = [
        ("dragon", "Dragon"),
        ("baron", "Baron"),
        ("tower", "Tower"),
        ("grubs", "Void Grubs"),
        ("herald", "Herald"),
    ]

    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    objective_type = models.CharField(
        max_length=20,
        choices=OBJECTIVE_CHOICES
    )

    minute = models.IntegerField()
    timestamp_seconds = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.objective_type} at {self.minute} min"


class Vod(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50)
    url = models.URLField()

    game_start_offset_seconds = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.provider} VOD for match {self.match_id}"
