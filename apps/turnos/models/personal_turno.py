from django.db import models

from apps.core.models import TimestampedModel
from apps.personal.models.personal import Personal
from apps.turnos.models.turno import Turno


class PersonalTurno(TimestampedModel):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="asignaciones_turno")
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT, related_name="asignaciones_personal")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "personal_turnos"
        ordering = ["-fecha_inicio"]


__all__ = ["PersonalTurno"]
