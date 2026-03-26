from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_reportes_personal"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="reporteasistenciadiaria",
            name="uq_reporte_asistencia_fecha",
        ),
        migrations.AddField(
            model_name="reporteasistenciadiaria",
            name="bloque_orden",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterModelOptions(
            name="reporteasistenciadiaria",
            options={"db_table": "reportes_asistencia_diaria", "ordering": ["reporte", "fecha", "bloque_orden"]},
        ),
        migrations.AddConstraint(
            model_name="reporteasistenciadiaria",
            constraint=models.UniqueConstraint(fields=("reporte", "fecha", "bloque_orden"), name="uq_reporte_asistencia_fecha_bloque"),
        ),
    ]
