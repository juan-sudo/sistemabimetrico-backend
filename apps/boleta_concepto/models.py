from django.db import models

from apps.boleta_mensual.models import BoletaMensual
from apps.core.models import TimestampedModel


class BoletaConcepto(TimestampedModel):
    class Tipo(models.TextChoices):
        INGRESO = "INGRESO", "Ingreso"
        DESCUENTO = "DESCUENTO", "Descuento"

    boleta = models.ForeignKey(BoletaMensual, on_delete=models.CASCADE, related_name="conceptos")
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    concepto = models.CharField(max_length=120)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "boletas_conceptos"
        ordering = ["boleta", "tipo", "concepto"]


__all__ = ["BoletaConcepto"]
