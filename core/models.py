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
