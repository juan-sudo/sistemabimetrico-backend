from django.db import models

from apps.core.models import TimestampedModel


class UbicacionGeografica(TimestampedModel):
    pais = models.CharField(max_length=80, default="Peru")
    departamento = models.CharField(max_length=80)
    provincia = models.CharField(max_length=80)
    distrito = models.CharField(max_length=80)

    class Meta:
        db_table = "ubicaciones_geograficas"
        ordering = ["departamento", "provincia", "distrito"]
        constraints = [
            models.UniqueConstraint(
                fields=["pais", "departamento", "provincia", "distrito"],
                name="uq_ubicacion_geo",
            )
        ]

    def __str__(self):
        return f"{self.departamento} / {self.provincia} / {self.distrito}"


__all__ = ["UbicacionGeografica"]
