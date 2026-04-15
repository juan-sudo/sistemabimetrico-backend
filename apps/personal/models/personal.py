from django.db import models

from apps.core.models import TimestampedModel


class Personal(TimestampedModel):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    empresa = models.ForeignKey("empresa.Empresa", on_delete=models.PROTECT, related_name="personales")
    sucursal = models.ForeignKey("sucursal.Sucursal", on_delete=models.PROTECT, related_name="personales")
    area = models.ForeignKey("area.Area", on_delete=models.PROTECT, related_name="personales")
    ubicacion = models.ForeignKey(
        "personal.UbicacionGeografica",
        on_delete=models.SET_NULL,
        related_name="personales",
        null=True,
        blank=True,
    )
    tipo_documento = models.ForeignKey("tipo_documento.TipoDocumento", on_delete=models.PROTECT, related_name="personales")
    tipo_trabajador = models.ForeignKey("tipo_trabajador.TipoTrabajador", on_delete=models.PROTECT, related_name="personales")
    categoria = models.ForeignKey("categoria.Categoria", on_delete=models.PROTECT, related_name="personales")
    tipo_sindicato = models.ForeignKey(
        "tipo_sindicato.TipoSindicato",
        on_delete=models.PROTECT,
        related_name="personales",
        null=True,
        blank=True,
    )
    cargo = models.ForeignKey("cargo.Cargo", on_delete=models.SET_NULL, related_name="personales", null=True, blank=True)
    codigo_empleado = models.CharField(max_length=30, unique=True)
    numero_documento = models.CharField(max_length=20, unique=True)
    nombres_completos = models.CharField(max_length=255)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)

    class Meta:
        db_table = "personales"
        ordering = ["nombres_completos"]

    def __str__(self):
        return f"{self.nombres_completos} ({self.numero_documento})"
