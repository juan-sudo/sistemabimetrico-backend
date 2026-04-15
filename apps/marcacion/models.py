from django.db import models

from apps.core.models import TimestampedModel


class Marcacion(TimestampedModel):
    class Situacion(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    class TipoEvento(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"

    personal = models.ForeignKey("personal.Personal", on_delete=models.CASCADE, related_name="marcaciones")
    dispositivo = models.ForeignKey(
        "personal.Dispositivo",
        on_delete=models.SET_NULL,
        related_name="marcaciones",
        null=True,
        blank=True,
    )
    descarga = models.ForeignKey(
        "descarga_marcacion.DescargaMarcacion",
        on_delete=models.SET_NULL,
        related_name="marcaciones",
        null=True,
        blank=True,
    )
    codigo_equipo = models.CharField(max_length=40, blank=True)
    fecha_hora = models.DateTimeField()
    tipo_evento = models.CharField(max_length=10, choices=TipoEvento.choices, default=TipoEvento.ENTRADA)
    situacion = models.CharField(max_length=10, choices=Situacion.choices, default=Situacion.ACTIVO)

    class Meta:
        db_table = "marcaciones"
        ordering = ["-fecha_hora"]
        indexes = [
            models.Index(fields=["fecha_hora"], name="idx_marcacion_fecha_hora"),
            models.Index(fields=["personal", "fecha_hora"], name="idx_marcacion_personal_fecha"),
            models.Index(fields=["situacion"], name="idx_marcacion_situacion"),
        ]


__all__ = ["Marcacion"]
