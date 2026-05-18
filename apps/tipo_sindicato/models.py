from django.db import models

from apps.core.models import TimestampedModel


class TipoSindicato(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "tipos_sindicato"
        ordering = ["descripcion"]
        indexes = [
            models.Index(fields=["descripcion"], name="idx_tipo_sind_desc"),
            models.Index(fields=["activo", "descripcion"], name="idx_tipo_sind_activo_desc"),
        ]

    def __str__(self):
        return self.descripcion


__all__ = ["TipoSindicato"]
