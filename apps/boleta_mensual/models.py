from django.db import models

from apps.core.models import TimestampedModel


class BoletaMensual(TimestampedModel):
    class Estado(models.TextChoices):
        GENERADA = "GENERADA", "Generada"
        DESCARGADA = "DESCARGADA", "Descargada"
        ANULADA = "ANULADA", "Anulada"

    personal = models.ForeignKey("personal.Personal", on_delete=models.CASCADE, related_name="boletas")
    anio = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2)
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    neto_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.GENERADA)
    archivo_pdf = models.FileField(upload_to="boletas/", blank=True, null=True)

    class Meta:
        db_table = "boletas_mensuales"
        ordering = ["-anio", "-mes"]
        constraints = [
            models.UniqueConstraint(fields=["personal", "anio", "mes"], name="uq_boleta_personal_periodo"),
            models.CheckConstraint(condition=models.Q(mes__gte=1, mes__lte=12), name="ck_boleta_mes_1_12"),
        ]


__all__ = ["BoletaMensual"]
