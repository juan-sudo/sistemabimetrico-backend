from django.db import models

from apps.core.models import TimestampedModel


class Categoria(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=120)
    periodos_vacacionales = models.BooleanField(default=False)
    dias_por_periodo = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "categorias"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


__all__ = ["Categoria"]
