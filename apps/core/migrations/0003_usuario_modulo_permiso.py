from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_area_hierarchy"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UsuarioModuloPermiso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("modulo", models.CharField(choices=[
                    ("ESCRITORIO", "Escritorio"),
                    ("EMPRESAS", "Empresas"),
                    ("SUCURSALES", "Sucursales"),
                    ("AREAS", "Areas"),
                    ("CARGOS", "Cargos"),
                    ("TIPO_TRABAJADOR", "Tipo trabajador"),
                    ("CATEGORIAS", "Categorias"),
                    ("TURNOS", "Turnos"),
                    ("DISPOSITIVOS", "Dispositivos"),
                    ("DESCARGAR_MARCAS", "Descargar marcas"),
                    ("PERSONAL", "Personal"),
                    ("BOLETA_MENSUAL", "Boleta mensual"),
                    ("RESUMEN_PLANILLA", "Resumen planilla"),
                    ("MARCACIONES", "Marcaciones"),
                    ("JUSTIFICACIONES", "Registrar justificacion"),
                    ("AUTORIZAR_JUSTIFICACION", "Autorizar justificacion"),
                    ("DESCANSO_MEDICO", "Descanso medico"),
                    ("USUARIOS", "Usuarios"),
                ], max_length=40)),
                ("puede_ver", models.BooleanField(default=True)),
                ("puede_crear", models.BooleanField(default=False)),
                ("puede_editar", models.BooleanField(default=False)),
                ("puede_eliminar", models.BooleanField(default=False)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="module_permissions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "usuarios_modulos_permisos",
                "ordering": ["user_id", "modulo"],
            },
        ),
        migrations.AddConstraint(
            model_name="usuariomodulopermiso",
            constraint=models.UniqueConstraint(fields=("user", "modulo"), name="uq_usuario_modulo_permiso"),
        ),
    ]
