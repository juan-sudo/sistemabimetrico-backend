from django.db import models

from apps.core.models import TimestampedModel


class DescansoMedico(TimestampedModel):
    class Motivo(models.TextChoices):
        SALUD = "SALUD", "Por salud"
        SUBSIDIO = "SUBSIDIO", "Subsidio"

    personal = models.ForeignKey("personal.Personal", on_delete=models.CASCADE, related_name="descansos_medicos")
    motivo = models.CharField(max_length=20, choices=Motivo.choices)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias = models.PositiveIntegerField(default=1)
    citt = models.CharField(max_length=60, blank=True)
    diagnostico = models.CharField(max_length=255, blank=True)
    tiene_adjunto = models.BooleanField(default=False)
    numero_documento = models.CharField(max_length=60, blank=True)

    class Meta:
        db_table = "descansos_medicos"
        ordering = ["-fecha_inicio"]


__all__ = ["DescansoMedico"]
