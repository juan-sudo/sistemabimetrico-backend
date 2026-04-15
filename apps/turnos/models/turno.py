from django.db import models

from apps.core.models import TimestampedModel


class Turno(TimestampedModel):
    class Tipo(models.TextChoices):
        GENERAL = "GENERAL", "General"
        GENERAL_PERSONALIZADO = "GENERAL_PERSONALIZADO", "General Personalizado"
        DESCANSO = "DESCANSO", "Descanso"

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=180)
    tipo = models.CharField(max_length=30, choices=Tipo.choices, default=Tipo.GENERAL)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "turnos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


__all__ = ["Turno"]
