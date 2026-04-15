from django.contrib import admin

from .models.personal_turno import PersonalTurno
from .models.turno import Turno
from .models.turno_bloque_horario import TurnoBloqueHorario

for model in [Turno, TurnoBloqueHorario, PersonalTurno]:
    admin.site.register(model)
