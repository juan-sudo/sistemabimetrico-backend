from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_usuario_modulo_permiso"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReportePersonalMensual",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("anio", models.PositiveSmallIntegerField()),
                ("mes", models.PositiveSmallIntegerField()),
                ("fecha_inicio", models.DateField()),
                ("fecha_fin", models.DateField()),
                ("sueldo_base", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("total_ingresos", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("total_descuentos", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("neto_pagar", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("total_dias_periodo", models.PositiveSmallIntegerField(default=0)),
                ("total_dias_laborados", models.PositiveSmallIntegerField(default=0)),
                ("total_dias_falta", models.PositiveSmallIntegerField(default=0)),
                ("total_dias_justificados", models.PositiveSmallIntegerField(default=0)),
                ("total_dias_descanso_medico", models.PositiveSmallIntegerField(default=0)),
                ("total_minutos_tardanza", models.PositiveIntegerField(default=0)),
                ("total_horas_trabajadas", models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ("total_horas_extra", models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                (
                    "estado",
                    models.CharField(
                        choices=[("BORRADOR", "Borrador"), ("GENERADO", "Generado"), ("CERRADO", "Cerrado")],
                        default="BORRADOR",
                        max_length=12,
                    ),
                ),
                ("observacion", models.CharField(blank=True, max_length=255)),
                ("archivo_pdf", models.FileField(blank=True, null=True, upload_to="reportes_personal/")),
                (
                    "personal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reportes_mensuales",
                        to="core.personal",
                    ),
                ),
            ],
            options={
                "db_table": "reportes_personal_mensual",
                "ordering": ["-anio", "-mes", "personal_id"],
            },
        ),
        migrations.CreateModel(
            name="ReporteAsistenciaDiaria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("fecha", models.DateField()),
                (
                    "estado_dia",
                    models.CharField(
                        choices=[
                            ("ASISTIO", "Asistio"),
                            ("FALTA", "Falta"),
                            ("JUSTIFICADO", "Justificado"),
                            ("DESCANSO_MEDICO", "Descanso medico"),
                            ("DESCANSO", "Descanso"),
                            ("FERIADO", "Feriado"),
                        ],
                        default="ASISTIO",
                        max_length=20,
                    ),
                ),
                ("hora_entrada_programada", models.TimeField(blank=True, null=True)),
                ("hora_salida_programada", models.TimeField(blank=True, null=True)),
                ("hora_entrada_real", models.TimeField(blank=True, null=True)),
                ("hora_salida_real", models.TimeField(blank=True, null=True)),
                ("minutos_tardanza", models.PositiveIntegerField(default=0)),
                ("horas_trabajadas", models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ("horas_extra", models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ("observacion", models.CharField(blank=True, max_length=255)),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dias",
                        to="core.reportepersonalmensual",
                    ),
                ),
            ],
            options={
                "db_table": "reportes_asistencia_diaria",
                "ordering": ["reporte", "fecha"],
            },
        ),
        migrations.CreateModel(
            name="ReporteConceptoPersonal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("INGRESO", "Ingreso"),
                            ("DESCUENTO", "Descuento"),
                            ("APORTE_TRABAJADOR", "Aporte trabajador"),
                            ("APORTE_EMPLEADOR", "Aporte empleador"),
                            ("OTRO", "Otro"),
                        ],
                        default="INGRESO",
                        max_length=20,
                    ),
                ),
                ("codigo", models.CharField(blank=True, max_length=20)),
                ("concepto", models.CharField(max_length=150)),
                ("monto", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("orden", models.PositiveSmallIntegerField(default=1)),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conceptos_reporte",
                        to="core.reportepersonalmensual",
                    ),
                ),
            ],
            options={
                "db_table": "reportes_conceptos_personal",
                "ordering": ["reporte", "orden", "tipo", "concepto"],
            },
        ),
        migrations.CreateModel(
            name="ReporteIncidenciaPersonal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("TARDANZA", "Tardanza"),
                            ("FALTA", "Falta"),
                            ("JUSTIFICACION", "Justificacion"),
                            ("DESCANSO_MEDICO", "Descanso medico"),
                            ("LICENCIA", "Licencia"),
                            ("OTRO", "Otro"),
                        ],
                        default="OTRO",
                        max_length=20,
                    ),
                ),
                ("fecha_inicio", models.DateField()),
                ("fecha_fin", models.DateField()),
                ("cantidad_dias", models.PositiveSmallIntegerField(default=0)),
                ("cantidad_minutos", models.PositiveIntegerField(default=0)),
                ("referencia_modelo", models.CharField(blank=True, max_length=50)),
                ("referencia_id", models.PositiveIntegerField(blank=True, null=True)),
                ("descripcion", models.TextField(blank=True)),
                ("observacion", models.CharField(blank=True, max_length=255)),
                (
                    "reporte",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incidencias",
                        to="core.reportepersonalmensual",
                    ),
                ),
            ],
            options={
                "db_table": "reportes_incidencias_personal",
                "ordering": ["reporte", "fecha_inicio", "tipo"],
            },
        ),
        migrations.AddConstraint(
            model_name="reportepersonalmensual",
            constraint=models.UniqueConstraint(fields=("personal", "anio", "mes"), name="uq_reporte_personal_periodo"),
        ),
        migrations.AddConstraint(
            model_name="reportepersonalmensual",
            constraint=models.CheckConstraint(condition=models.Q(("mes__gte", 1), ("mes__lte", 12)), name="ck_reporte_mes_1_12"),
        ),
        migrations.AddConstraint(
            model_name="reporteasistenciadiaria",
            constraint=models.UniqueConstraint(fields=("reporte", "fecha"), name="uq_reporte_asistencia_fecha"),
        ),
    ]
