from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import TimestampedModel


User = get_user_model()


class UsuarioModuloPermiso(TimestampedModel):
    class Modulo(models.TextChoices):
        ESCRITORIO = "ESCRITORIO", "Escritorio"
        EMPRESAS = "EMPRESAS", "Empresas"
        SUCURSALES = "SUCURSALES", "Sucursales"
        AREAS = "AREAS", "Areas"
        CARGOS = "CARGOS", "Cargos"
        TIPO_TRABAJADOR = "TIPO_TRABAJADOR", "Tipo trabajador"
        TIPO_SINDICATO = "TIPO_SINDICATO", "Tipo sindicato"
        CATEGORIAS = "CATEGORIAS", "Categorias"
        TURNOS = "TURNOS", "Turnos"
        DISPOSITIVOS = "DISPOSITIVOS", "Dispositivos"
        DESCARGAR_MARCAS = "DESCARGAR_MARCAS", "Descargar marcas"
        PERSONAL = "PERSONAL", "Personal"
        BOLETA_MENSUAL = "BOLETA_MENSUAL", "Boleta mensual"
        RESUMEN_PLANILLA = "RESUMEN_PLANILLA", "Resumen planilla"
        MARCACIONES = "MARCACIONES", "Marcaciones"
        PROCESAR_ASISTENCIA = "PROCESAR_ASISTENCIA", "Procesar asistencia"
        CONSULTAR_ASISTENCIA = "CONSULTAR_ASISTENCIA", "Consultar asistencia"
        JUSTIFICACIONES = "JUSTIFICACIONES", "Registrar justificacion"
        AUTORIZAR_JUSTIFICACION = "AUTORIZAR_JUSTIFICACION", "Autorizar justificacion"
        DESCANSO_MEDICO = "DESCANSO_MEDICO", "Descanso medico"
        USUARIOS = "USUARIOS", "Usuarios"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_permissions")
    modulo = models.CharField(max_length=40, choices=Modulo.choices)
    puede_ver = models.BooleanField(default=True)
    puede_crear = models.BooleanField(default=False)
    puede_editar = models.BooleanField(default=False)
    puede_eliminar = models.BooleanField(default=False)

    class Meta:
        db_table = "usuarios_modulos_permisos"
        ordering = ["user_id", "modulo"]
        constraints = [
            models.UniqueConstraint(fields=["user", "modulo"], name="uq_usuario_modulo_permiso"),
        ]


__all__ = ["User", "UsuarioModuloPermiso"]
