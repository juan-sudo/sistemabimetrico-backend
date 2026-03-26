from django.db import migrations


def seed_tipos_documento(apps, schema_editor):
    TipoDocumento = apps.get_model("core", "TipoDocumento")
    defaults = [
        ("CE", "CARNE DE EXTRANJERIA"),
        ("CDI", "CARNE DE IDENTIDAD - RELACIONES EXTERIORES"),
        ("DNI", "DOCUMENTO NACIONAL DE IDENTIDAD"),
        ("PN", "PARTIDA DE NACIMIENTO"),
        ("PAS", "PASAPORTE"),
        ("RUC", "REG. UNICO DE CONTRIBUYENTES"),
    ]
    for codigo, descripcion in defaults:
        TipoDocumento.objects.update_or_create(
            codigo=codigo,
            defaults={
                "descripcion": descripcion,
                "activo": True,
            },
        )


def unseed_tipos_documento(apps, schema_editor):
    TipoDocumento = apps.get_model("core", "TipoDocumento")
    TipoDocumento.objects.filter(codigo__in=["CE", "CDI", "DNI", "PN", "PAS", "RUC"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_usuario_modulo_tipo_sindicato"),
    ]

    operations = [
        migrations.RunPython(seed_tipos_documento, unseed_tipos_documento),
    ]

