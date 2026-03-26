from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_usuario_modulo_reporte"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuariomodulopermiso",
            name="modulo",
            field=models.CharField(
                choices=[
                    ("ESCRITORIO", "Escritorio"),
                    ("EMPRESAS", "Empresas"),
                    ("SUCURSALES", "Sucursales"),
                    ("AREAS", "Areas"),
                    ("CARGOS", "Cargos"),
                    ("TIPO_TRABAJADOR", "Tipo trabajador"),
                    ("TIPO_SINDICATO", "Tipo sindicato"),
                    ("CATEGORIAS", "Categorias"),
                    ("TURNOS", "Turnos"),
                    ("DISPOSITIVOS", "Dispositivos"),
                    ("DESCARGAR_MARCAS", "Descargar marcas"),
                    ("PERSONAL", "Personal"),
                    ("BOLETA_MENSUAL", "Boleta mensual"),
                    ("RESUMEN_PLANILLA", "Resumen planilla"),
                    ("MARCACIONES", "Marcaciones"),
                    ("PROCESAR_ASISTENCIA", "Procesar asistencia"),
                    ("CONSULTAR_ASISTENCIA", "Consultar asistencia"),
                    ("JUSTIFICACIONES", "Registrar justificacion"),
                    ("AUTORIZAR_JUSTIFICACION", "Autorizar justificacion"),
                    ("DESCANSO_MEDICO", "Descanso medico"),
                    ("USUARIOS", "Usuarios"),
                ],
                max_length=40,
            ),
        ),
    ]
