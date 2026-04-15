from django.db import models

from apps.core.models import TimestampedModel


class Cargo(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "cargos"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


__all__ = ["Cargo"]
