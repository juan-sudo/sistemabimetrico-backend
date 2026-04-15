from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ApiRootView,
    DashboardResumenView,
    HealthCheckView,
    ReporteAsistenciaDiariaViewSet,
    ReporteConceptoPersonalViewSet,
    ReporteIncidenciaPersonalViewSet,
    ReportePersonalMensualViewSet,
)

router = DefaultRouter()
router.register("reportes-personal", ReportePersonalMensualViewSet, basename="reportes-personal")
router.register("reportes-asistencia-diaria", ReporteAsistenciaDiariaViewSet, basename="reportes-asistencia-diaria")
router.register("reportes-conceptos", ReporteConceptoPersonalViewSet, basename="reportes-conceptos")
router.register("reportes-incidencias", ReporteIncidenciaPersonalViewSet, basename="reportes-incidencias")

urlpatterns = [
    path("", ApiRootView.as_view(), name="api-root"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("dashboard-resumen/", DashboardResumenView.as_view(), name="dashboard-resumen"),
    *router.urls,
]
