from django.urls import path

from apps.asistencia_diaria.api.urls import urlpatterns as asistencia_diaria_urlpatterns
from apps.area.api.urls import urlpatterns as area_urlpatterns
from apps.accounts.api.urls import urlpatterns as accounts_urlpatterns
from apps.boleta_concepto.api.urls import urlpatterns as boleta_concepto_urlpatterns
from apps.boleta_mensual.api.urls import urlpatterns as boleta_mensual_urlpatterns
from apps.cargo.api.urls import urlpatterns as cargo_urlpatterns
from apps.categoria.api.urls import urlpatterns as categoria_urlpatterns
from apps.descanso_medico.api.urls import urlpatterns as descanso_medico_urlpatterns
from apps.descarga_marcacion.api.urls import urlpatterns as descarga_marcacion_urlpatterns
from apps.dispositivo.api.urls import urlpatterns as dispositivo_urlpatterns
from apps.empresa.api.urls import urlpatterns as empresa_urlpatterns
from apps.justificacion.api.urls import urlpatterns as justificacion_urlpatterns
from apps.marcacion.api.urls import urlpatterns as marcacion_urlpatterns
from apps.personal.api.urls import urlpatterns as personal_urlpatterns
from apps.reportes.api.urls import urlpatterns as reportes_urlpatterns
from apps.sucursal.api.urls import urlpatterns as sucursal_urlpatterns
from apps.tipo_documento.api.urls import urlpatterns as tipo_documento_urlpatterns
from apps.tipo_sindicato.api.urls import urlpatterns as tipo_sindicato_urlpatterns
from apps.tipo_trabajador.api.urls import urlpatterns as tipo_trabajador_urlpatterns
from apps.turnos.api.urls import urlpatterns as turnos_urlpatterns
from apps.usuario.api.urls import urlpatterns as usuario_urlpatterns

urlpatterns = [
    *asistencia_diaria_urlpatterns,
    *area_urlpatterns,
    *accounts_urlpatterns,
    *boleta_concepto_urlpatterns,
    *boleta_mensual_urlpatterns,
    *cargo_urlpatterns,
    *categoria_urlpatterns,
    *descanso_medico_urlpatterns,
    *descarga_marcacion_urlpatterns,
    *dispositivo_urlpatterns,
    *empresa_urlpatterns,
    *justificacion_urlpatterns,
    *marcacion_urlpatterns,
    *personal_urlpatterns,
    *reportes_urlpatterns,
    *sucursal_urlpatterns,
    *tipo_documento_urlpatterns,
    *tipo_sindicato_urlpatterns,
    *tipo_trabajador_urlpatterns,
    *turnos_urlpatterns,
    *usuario_urlpatterns,
]
