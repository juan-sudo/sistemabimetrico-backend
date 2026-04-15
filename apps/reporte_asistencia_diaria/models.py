from django.db import models

from apps.core.models import TimestampedModel
from apps.reporte_personal_mensual.models import ReportePersonalMensual


class ReporteAsistenciaDiaria(TimestampedModel):
    class EstadoDia(models.TextChoices):
        ASISTIO = "ASISTIO", "Asistio"
        FALTA = "FALTA", "Falta"
        JUSTIFICADO = "JUSTIFICADO", "Justificado"
        DESCANSO_MEDICO = "DESCANSO_MEDICO", "Descanso medico"
        DESCANSO = "DESCANSO", "Descanso"
        FERIADO = "FERIADO", "Feriado"

    reporte = models.ForeignKey(ReportePersonalMensual, on_delete=models.CASCADE, related_name="dias")
    fecha = models.DateField()
    bloque_orden = models.PositiveSmallIntegerField(default=1)
    estado_dia = models.CharField(max_length=20, choices=EstadoDia.choices, default=EstadoDia.ASISTIO)
    hora_entrada_programada = models.TimeField(null=True, blank=True)
    hora_salida_programada = models.TimeField(null=True, blank=True)
    hora_entrada_real = models.TimeField(null=True, blank=True)
    hora_salida_real = models.TimeField(null=True, blank=True)
    minutos_tardanza = models.PositiveIntegerField(default=0)
    horas_trabajadas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    horas_extra = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "reportes_asistencia_diaria"
        ordering = ["reporte", "fecha", "bloque_orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["reporte", "fecha", "bloque_orden"],
                name="uq_reporte_asistencia_fecha_bloque",
            ),
        ]

    def __str__(self):
        return f"{self.reporte.personal.nombres_completos} - {self.fecha} - Bloque {self.bloque_orden}"


__all__ = ["ReporteAsistenciaDiaria"]
