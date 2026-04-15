from apps.asistencia_diaria.selectors import (
    filter_asistencia_diaria_queryset,
    get_asistencia_diaria_queryset,
)
from apps.asistencia_diaria.serializers import AsistenciaDiariaSerializer
from apps.core.api import BaseModelViewSet
from apps.reporte_asistencia_diaria.models import ReporteAsistenciaDiaria


class AsistenciaDiariaViewSet(BaseModelViewSet):
    queryset = ReporteAsistenciaDiaria.objects.all()
    serializer_class = AsistenciaDiariaSerializer

    def get_queryset(self):
        queryset = get_asistencia_diaria_queryset()
        return filter_asistencia_diaria_queryset(
            queryset,
            reporte=self.request.query_params.get("reporte"),
            personal=self.request.query_params.get("personal"),
            anio=self.request.query_params.get("anio"),
            mes=self.request.query_params.get("mes"),
            fecha_inicio=self.request.query_params.get("fecha_inicio"),
            fecha_fin=self.request.query_params.get("fecha_fin"),
            estado_dia=self.request.query_params.get("estado_dia"),
        ).order_by("fecha", "bloque_orden", "reporte__personal__nombres_completos")


__all__ = ["AsistenciaDiariaViewSet"]
