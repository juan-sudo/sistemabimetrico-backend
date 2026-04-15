from django.db import models

from apps.core.models import TimestampedModel


class Dispositivo(TimestampedModel):
    class DireccionTipo(models.TextChoices):
        IP = "IP", "Direccion IP"
        DOMINIO = "DOMINIO", "Dominio"

    class Uso(models.TextChoices):
        ASISTENCIA = "ASISTENCIA", "Control de Asistencia"
        ACCESO = "ACCESO", "Control de Acceso"

    nombre = models.CharField(max_length=120, unique=True)
    direccion_tipo = models.CharField(max_length=10, choices=DireccionTipo.choices, default=DireccionTipo.IP)
    direccion = models.CharField(max_length=255)
    comunicacion = models.CharField(max_length=40, default="TCP/IP")
    puerto = models.PositiveIntegerField(default=4370)
    uso = models.CharField(max_length=20, choices=Uso.choices, default=Uso.ASISTENCIA)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "dispositivos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


__all__ = ["Dispositivo"]
