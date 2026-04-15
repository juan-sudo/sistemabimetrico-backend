from apps.core.api import BaseModelViewSet
from apps.reporte_asistencia_diaria.models import ReporteAsistenciaDiaria
from apps.reporte_asistencia_diaria.selectors import (
    filter_reporte_asistencia_diaria_queryset,
    get_reporte_asistencia_diaria_queryset,
)
from apps.reporte_asistencia_diaria.serializers import ReporteAsistenciaDiariaSerializer


class ReporteAsistenciaDiariaViewSet(BaseModelViewSet):
    queryset = ReporteAsistenciaDiaria.objects.all()
    serializer_class = ReporteAsistenciaDiariaSerializer

    def get_queryset(self):
        queryset = get_reporte_asistencia_diaria_queryset()
        return filter_reporte_asistencia_diaria_queryset(
            queryset,
            reporte=self.request.query_params.get("reporte"),
            personal=self.request.query_params.get("personal"),
            anio=self.request.query_params.get("anio"),
            mes=self.request.query_params.get("mes"),
            fecha_inicio=self.request.query_params.get("fecha_inicio"),
            fecha_fin=self.request.query_params.get("fecha_fin"),
            estado_dia=self.request.query_params.get("estado_dia"),
        ).order_by("fecha", "bloque_orden", "reporte__personal__nombres_completos")


__all__ = ["ReporteAsistenciaDiariaViewSet"]
