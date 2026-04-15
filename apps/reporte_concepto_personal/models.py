from django.db import models

from apps.core.models import TimestampedModel
from apps.reporte_personal_mensual.models import ReportePersonalMensual


class ReporteConceptoPersonal(TimestampedModel):
    class Tipo(models.TextChoices):
        INGRESO = "INGRESO", "Ingreso"
        DESCUENTO = "DESCUENTO", "Descuento"
        APORTE_TRABAJADOR = "APORTE_TRABAJADOR", "Aporte trabajador"
        APORTE_EMPLEADOR = "APORTE_EMPLEADOR", "Aporte empleador"
        OTRO = "OTRO", "Otro"

    reporte = models.ForeignKey(ReportePersonalMensual, on_delete=models.CASCADE, related_name="conceptos_reporte")
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.INGRESO)
    codigo = models.CharField(max_length=20, blank=True)
    concepto = models.CharField(max_length=150)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "reportes_conceptos_personal"
        ordering = ["reporte", "orden", "tipo", "concepto"]

    def __str__(self):
        return f"{self.reporte.personal.nombres_completos} - {self.concepto} ({self.monto})"


__all__ = ["ReporteConceptoPersonal"]
