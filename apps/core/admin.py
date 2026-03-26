from django.contrib import admin

from . import models


MODELS = [
    models.Empresa,
    models.Sucursal,
    models.Area,
    models.Cargo,
    models.TipoTrabajador,
    models.Categoria,
    models.TipoDocumento,
    models.TipoSindicato,
    models.UbicacionGeografica,
    models.Personal,
    models.Turno,
    models.TurnoBloqueHorario,
    models.PersonalTurno,
    models.Dispositivo,
    models.DescargaMarcacion,
    models.Marcacion,
    models.Justificacion,
    models.DescansoMedico,
    models.BoletaMensual,
    models.BoletaConcepto,
    models.UsuarioAgua,
    models.LicenciaAgua,
]

for model in MODELS:
    admin.site.register(model)
