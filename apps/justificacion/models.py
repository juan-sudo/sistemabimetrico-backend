from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import TimestampedModel


User = get_user_model()


class Justificacion(TimestampedModel):
    class Tipo(models.TextChoices):
        SALIDA = "SALIDA", "Salida"
        INGRESO = "INGRESO", "Ingreso"

    class Rango(models.TextChoices):
        PARCIAL = "PARCIAL", "Parcial"
        COMPLETO = "COMPLETO", "Completo"

    class Estado(models.TextChoices):
        AUTORIZADO = "AUTORIZADO", "Autorizado"
        NO_AUTORIZADO = "NO_AUTORIZADO", "No Autorizado"
        PENDIENTE = "PENDIENTE", "Pendiente"

    personal = models.ForeignKey("personal.Personal", on_delete=models.CASCADE, related_name="justificaciones")
    sucursal = models.ForeignKey("sucursal.Sucursal", on_delete=models.PROTECT, related_name="justificaciones")
    area = models.ForeignKey("area.Area", on_delete=models.PROTECT, related_name="justificaciones")
    motivo = models.CharField(max_length=180)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.SALIDA)
    rango = models.CharField(max_length=10, choices=Rango.choices, default=Rango.PARCIAL)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias = models.PositiveIntegerField(default=1)
    descripcion = models.TextField(blank=True)
    tiene_adjunto = models.BooleanField(default=False)
    numero_documento = models.CharField(max_length=50, blank=True)
    nombre_documento = models.CharField(max_length=180, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    gestionado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_gestion = models.DateTimeField(null=True, blank=True)
    motivo_no_autorizacion = models.TextField(blank=True)

    class Meta:
        db_table = "justificaciones"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["estado"], name="idx_justificacion_estado"),
            models.Index(fields=["fecha_inicio"], name="idx_justificacion_fecha_ini"),
            models.Index(fields=["fecha_fin"], name="idx_justificacion_fecha_fin"),
            models.Index(fields=["estado", "fecha_inicio", "fecha_fin"], name="idx_justif_estado_rango"),
            models.Index(fields=["personal", "fecha_inicio", "fecha_fin"], name="idx_justif_personal_rango"),
        ]


__all__ = ["Justificacion"]
