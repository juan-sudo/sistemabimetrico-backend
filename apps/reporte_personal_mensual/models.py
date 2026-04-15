from django.db import models

from apps.core.models import TimestampedModel
from apps.personal.models.personal import Personal


class ReportePersonalMensual(TimestampedModel):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        GENERADO = "GENERADO", "Generado"
        CERRADO = "CERRADO", "Cerrado"

    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="reportes_mensuales")
    anio = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    neto_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_dias_periodo = models.PositiveSmallIntegerField(default=0)
    total_dias_laborados = models.PositiveSmallIntegerField(default=0)
    total_dias_falta = models.PositiveSmallIntegerField(default=0)
    total_dias_justificados = models.PositiveSmallIntegerField(default=0)
    total_dias_descanso_medico = models.PositiveSmallIntegerField(default=0)
    total_minutos_tardanza = models.PositiveIntegerField(default=0)
    total_horas_trabajadas = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    total_horas_extra = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.BORRADOR)
    observacion = models.CharField(max_length=255, blank=True)
    archivo_pdf = models.FileField(upload_to="reportes_personal/", blank=True, null=True)

    class Meta:
        db_table = "reportes_personal_mensual"
        ordering = ["-anio", "-mes", "personal_id"]
        constraints = [
            models.UniqueConstraint(fields=["personal", "anio", "mes"], name="uq_reporte_personal_periodo"),
            models.CheckConstraint(condition=models.Q(mes__gte=1, mes__lte=12), name="ck_reporte_mes_1_12"),
        ]

    def __str__(self):
        return f"{self.personal.nombres_completos} - {self.mes:02d}/{self.anio}"


__all__ = ["ReportePersonalMensual"]
