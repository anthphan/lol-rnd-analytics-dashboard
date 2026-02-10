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
    assits = models.IntegerField()

    cs = models.IntegerField()
    gold = models.IntegerField()

    def __str__(self):
        return f"{self.player} in match {self.match}"
