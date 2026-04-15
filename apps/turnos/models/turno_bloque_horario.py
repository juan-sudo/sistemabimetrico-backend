from django.db import models

from apps.core.models import TimestampedModel
from apps.turnos.models.turno import Turno


class TurnoBloqueHorario(TimestampedModel):
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name="bloques")
    orden = models.PositiveSmallIntegerField(default=1)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()

    class Meta:
        db_table = "turno_bloques_horario"
        ordering = ["turno", "orden"]
        constraints = [
            models.UniqueConstraint(fields=["turno", "orden"], name="uq_turno_bloque_orden"),
        ]

    def __str__(self):
        return f"{self.turno.codigo} bloque {self.orden}"


__all__ = ["TurnoBloqueHorario"]
