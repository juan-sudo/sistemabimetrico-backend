from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from apps.area.models import Area
from apps.area.serializers import AreaSerializer
from apps.core.api import BaseModelViewSet


class AreaPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class AreaViewSet(BaseModelViewSet):
    queryset = Area.objects.select_related("sucursal", "sucursal__empresa", "parent").only(
        "id",
        "sucursal_id",
        "sucursal__id",
        "sucursal__nombre",
        "sucursal__empresa_id",
        "sucursal__empresa__razon_social",
        "codigo",
        "nombre",
        "tipo",
        "parent_id",
        "activo",
    )
    serializer_class = AreaSerializer
    pagination_class = AreaPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        empresa = (self.request.query_params.get("empresa") or "").strip()
        sucursal = (self.request.query_params.get("sucursal") or "").strip()
        q = (self.request.query_params.get("q") or self.request.query_params.get("search") or "").strip()
        activo = (self.request.query_params.get("activo") or "").strip().lower()

        if empresa:
            queryset = queryset.filter(sucursal__empresa_id=empresa)
        if sucursal:
            queryset = queryset.filter(sucursal_id=sucursal)
        if activo in {"1", "true", "si", "sí", "activo"}:
            queryset = queryset.filter(activo=True)
        elif activo in {"0", "false", "no", "inactivo"}:
            queryset = queryset.filter(activo=False)
        if q:
            queryset = queryset.filter(
                Q(codigo__icontains=q)
                | Q(nombre__icontains=q)
                | Q(tipo__icontains=q)
                | Q(parent__nombre__icontains=q)
                | Q(sucursal__nombre__icontains=q)
            )

        return queryset.order_by("nombre")
