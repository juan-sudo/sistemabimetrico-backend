from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import TimestampedModel


User = get_user_model()


class DescargaMarcacion(TimestampedModel):
    class Fuente(models.TextChoices):
        DISPOSITIVO = "DISPOSITIVO", "Dispositivo"
        USB = "USB", "USB"
        EXCEL = "EXCEL", "Importacion Excel"

    dispositivo = models.ForeignKey(
        "personal.Dispositivo",
        on_delete=models.SET_NULL,
        related_name="descargas",
        null=True,
        blank=True,
    )
    fuente = models.CharField(max_length=20, choices=Fuente.choices, default=Fuente.DISPOSITIVO)
    ejecutado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "descargas_marcaciones"
        ordering = ["-created_at"]


__all__ = ["DescargaMarcacion"]
