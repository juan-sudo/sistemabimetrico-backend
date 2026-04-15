from apps.core.api import BaseModelViewSet
from apps.reporte_incidencia_personal.models import ReporteIncidenciaPersonal
from apps.reporte_incidencia_personal.selectors import (
    filter_reporte_incidencia_personal_queryset,
    get_reporte_incidencia_personal_queryset,
)
from apps.reporte_incidencia_personal.serializers import ReporteIncidenciaPersonalSerializer


class ReporteIncidenciaPersonalViewSet(BaseModelViewSet):
    queryset = ReporteIncidenciaPersonal.objects.all()
    serializer_class = ReporteIncidenciaPersonalSerializer

    def get_queryset(self):
        queryset = get_reporte_incidencia_personal_queryset()
        return filter_reporte_incidencia_personal_queryset(
            queryset,
            reporte=self.request.query_params.get("reporte"),
            personal=self.request.query_params.get("personal"),
            anio=self.request.query_params.get("anio"),
            mes=self.request.query_params.get("mes"),
            tipo=self.request.query_params.get("tipo"),
            fecha_inicio=self.request.query_params.get("fecha_inicio"),
            fecha_fin=self.request.query_params.get("fecha_fin"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("reporte__personal__nombres_completos", "fecha_inicio", "tipo")


__all__ = ["ReporteIncidenciaPersonalViewSet"]
