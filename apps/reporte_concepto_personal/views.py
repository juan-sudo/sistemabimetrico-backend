from apps.core.api import BaseModelViewSet
from apps.reporte_concepto_personal.models import ReporteConceptoPersonal
from apps.reporte_concepto_personal.selectors import (
    filter_reporte_concepto_personal_queryset,
    get_reporte_concepto_personal_queryset,
)
from apps.reporte_concepto_personal.serializers import ReporteConceptoPersonalSerializer


class ReporteConceptoPersonalViewSet(BaseModelViewSet):
    queryset = ReporteConceptoPersonal.objects.all()
    serializer_class = ReporteConceptoPersonalSerializer

    def get_queryset(self):
        queryset = get_reporte_concepto_personal_queryset()
        return filter_reporte_concepto_personal_queryset(
            queryset,
            reporte=self.request.query_params.get("reporte"),
            personal=self.request.query_params.get("personal"),
            anio=self.request.query_params.get("anio"),
            mes=self.request.query_params.get("mes"),
            tipo=self.request.query_params.get("tipo"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("reporte__personal__nombres_completos", "orden", "tipo", "concepto")


__all__ = ["ReporteConceptoPersonalViewSet"]
