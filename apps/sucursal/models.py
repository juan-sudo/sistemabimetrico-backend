from django.db import models

from apps.core.models import TimestampedModel


class Sucursal(TimestampedModel):
    empresa = models.ForeignKey("empresa.Empresa", on_delete=models.CASCADE, related_name="sucursales")
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "sucursales"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["empresa", "codigo"], name="uq_sucursal_empresa_codigo"),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


__all__ = ["Sucursal"]
