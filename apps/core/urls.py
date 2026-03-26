from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    AreaViewSet,
    BoletaConceptoViewSet,
    BoletaMensualViewSet,
    CargoViewSet,
    CategoriaViewSet,
    DescansoMedicoViewSet,
    DescargaMarcacionViewSet,
    DispositivoViewSet,
    EmpresaViewSet,
    JustificacionViewSet,
    LicenciaAguaViewSet,
    LoginView,
    MarcacionViewSet,
    MeView,
    PersonalTurnoViewSet,
    PersonalViewSet,
    ReporteAsistenciaDiariaViewSet,
    ReporteConceptoPersonalViewSet,
    ReporteIncidenciaPersonalViewSet,
    ReportePersonalMensualViewSet,
    SucursalViewSet,
    TipoDocumentoViewSet,
    TipoSindicatoViewSet,
    TipoTrabajadorViewSet,
    TurnoBloqueHorarioViewSet,
    TurnoViewSet,
    UbicacionGeograficaViewSet,
    UsuarioViewSet,
    UsuarioAguaViewSet,
    api_root,
    health_check,
)

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuarios")
router.register("empresas", EmpresaViewSet, basename="empresas")
router.register("sucursales", SucursalViewSet, basename="sucursales")
router.register("areas", AreaViewSet, basename="areas")
router.register("cargos", CargoViewSet, basename="cargos")
router.register("tipos-trabajador", TipoTrabajadorViewSet, basename="tipos-trabajador")
router.register("categorias", CategoriaViewSet, basename="categorias")
router.register("tipos-documento", TipoDocumentoViewSet, basename="tipos-documento")
router.register("tipos-sindicato", TipoSindicatoViewSet, basename="tipos-sindicato")
router.register("ubicaciones-geograficas", UbicacionGeograficaViewSet, basename="ubicaciones-geograficas")
router.register("personales", PersonalViewSet, basename="personales")
router.register("turnos", TurnoViewSet, basename="turnos")
router.register("turno-bloques-horario", TurnoBloqueHorarioViewSet, basename="turno-bloques-horario")
router.register("personal-turnos", PersonalTurnoViewSet, basename="personal-turnos")
router.register("dispositivos", DispositivoViewSet, basename="dispositivos")
router.register("descargas-marcaciones", DescargaMarcacionViewSet, basename="descargas-marcaciones")
router.register("marcaciones", MarcacionViewSet, basename="marcaciones")
router.register("justificaciones", JustificacionViewSet, basename="justificaciones")
router.register("descansos-medicos", DescansoMedicoViewSet, basename="descansos-medicos")
router.register("boletas-mensuales", BoletaMensualViewSet, basename="boletas-mensuales")
router.register("boletas-conceptos", BoletaConceptoViewSet, basename="boletas-conceptos")
router.register("reportes-personal", ReportePersonalMensualViewSet, basename="reportes-personal")
router.register("reportes-asistencia-diaria", ReporteAsistenciaDiariaViewSet, basename="reportes-asistencia-diaria")
router.register("reportes-conceptos", ReporteConceptoPersonalViewSet, basename="reportes-conceptos")
router.register("reportes-incidencias", ReporteIncidenciaPersonalViewSet, basename="reportes-incidencias")
router.register("usuarios-agua", UsuarioAguaViewSet, basename="usuarios-agua")
router.register("licencias-agua", LicenciaAguaViewSet, basename="licencias-agua")

urlpatterns = [
    path("", api_root, name="api-root"),
    path("health/", health_check, name="health-check"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]
