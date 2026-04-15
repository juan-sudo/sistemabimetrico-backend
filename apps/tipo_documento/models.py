from django.db import models

from apps.core.models import TimestampedModel


class TipoDocumento(TimestampedModel):
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "tipos_documento"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


__all__ = ["TipoDocumento"]
