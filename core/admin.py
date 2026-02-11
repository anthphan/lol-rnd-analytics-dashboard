from django.contrib import admin
from .models import Team, Player, Match, PlayerMatchStats, ObjectiveEvent, Vod

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(PlayerMatchStats)
admin.site.register(ObjectiveEvent)
admin.site.register(Vod)

# Register your models here.
