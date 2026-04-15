from django.db import models

from apps.core.models import TimestampedModel


class Empresa(TimestampedModel):
    codigo = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)
    ruc = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(blank=True)
    logo = models.FileField(upload_to="empresas/logos/", blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "empresas"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social


__all__ = ["Empresa"]
