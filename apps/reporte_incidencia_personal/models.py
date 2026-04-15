from django.db import models

from apps.core.models import TimestampedModel
from apps.reporte_personal_mensual.models import ReportePersonalMensual


class ReporteIncidenciaPersonal(TimestampedModel):
    class Tipo(models.TextChoices):
        TARDANZA = "TARDANZA", "Tardanza"
        FALTA = "FALTA", "Falta"
        JUSTIFICACION = "JUSTIFICACION", "Justificacion"
        DESCANSO_MEDICO = "DESCANSO_MEDICO", "Descanso medico"
        LICENCIA = "LICENCIA", "Licencia"
        OTRO = "OTRO", "Otro"

    reporte = models.ForeignKey(ReportePersonalMensual, on_delete=models.CASCADE, related_name="incidencias")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.OTRO)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad_dias = models.PositiveSmallIntegerField(default=0)
    cantidad_minutos = models.PositiveIntegerField(default=0)
    referencia_modelo = models.CharField(max_length=50, blank=True)
    referencia_id = models.PositiveIntegerField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "reportes_incidencias_personal"
        ordering = ["reporte", "fecha_inicio", "tipo"]

    def __str__(self):
        return f"{self.reporte.personal.nombres_completos} - {self.tipo} - {self.fecha_inicio}"


__all__ = ["ReporteIncidenciaPersonal"]
