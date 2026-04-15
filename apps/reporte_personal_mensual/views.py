from apps.core.api import BaseModelViewSet
from apps.reporte_personal_mensual.models import ReportePersonalMensual
from apps.reporte_personal_mensual.selectors import (
    filter_reporte_personal_mensual_queryset,
    get_reporte_personal_mensual_queryset,
)
from apps.reporte_personal_mensual.serializers import ReportePersonalMensualSerializer


class ReportePersonalMensualViewSet(BaseModelViewSet):
    queryset = ReportePersonalMensual.objects.all()
    serializer_class = ReportePersonalMensualSerializer

    def get_queryset(self):
        queryset = get_reporte_personal_mensual_queryset()
        return filter_reporte_personal_mensual_queryset(
            queryset,
            personal=self.request.query_params.get("personal"),
            empresa=self.request.query_params.get("empresa"),
            sucursal=self.request.query_params.get("sucursal"),
            area=self.request.query_params.get("area"),
            anio=self.request.query_params.get("anio"),
            mes=self.request.query_params.get("mes"),
            estado=self.request.query_params.get("estado"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("-anio", "-mes", "personal__nombres_completos")


__all__ = ["ReportePersonalMensualViewSet"]
