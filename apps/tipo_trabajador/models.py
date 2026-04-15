from django.db import models

from apps.core.models import TimestampedModel


class TipoTrabajador(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "tipos_trabajador"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


__all__ = ["TipoTrabajador"]
