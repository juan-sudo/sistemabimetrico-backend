from django.db import models

from apps.core.models import TimestampedModel


class Area(TimestampedModel):
    class Tipo(models.TextChoices):
        GERENCIA = "GERENCIA", "Gerencia"
        OFICINA = "OFICINA", "Oficina"
        SUBGERENCIA = "SUBGERENCIA", "Subgerencia"
        UNIDAD = "UNIDAD", "Unidad"

    sucursal = models.ForeignKey("sucursal.Sucursal", on_delete=models.CASCADE, related_name="areas")
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.GERENCIA)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        null=True,
        blank=True,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "areas"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["sucursal", "codigo"], name="uq_area_sucursal_codigo"),
        ]
        indexes = [
            models.Index(fields=["nombre"], name="idx_area_nombre"),
            models.Index(fields=["sucursal", "nombre"], name="idx_area_sucursal_nombre"),
            models.Index(fields=["activo", "nombre"], name="idx_area_activo_nombre"),
            models.Index(fields=["tipo", "sucursal"], name="idx_area_tipo_sucursal"),
        ]

    def __str__(self):
        return self.nombre


__all__ = ["Area"]
