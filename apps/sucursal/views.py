from rest_framework.pagination import PageNumberPagination

from apps.core.api import BaseModelViewSet
from apps.sucursal.models import Sucursal
from apps.sucursal.selectors import filter_sucursal_queryset
from apps.sucursal.serializers import SucursalSerializer


class SucursalPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class SucursalViewSet(BaseModelViewSet):
    queryset = Sucursal.objects.select_related("empresa").only(
        "id",
        "empresa_id",
        "empresa__codigo",
        "empresa__razon_social",
        "codigo",
        "nombre",
        "activo",
    )
    serializer_class = SucursalSerializer
    pagination_class = SucursalPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_sucursal_queryset(
            queryset,
            empresa=self.request.query_params.get("empresa"),
            activo=self.request.query_params.get("activo"),
            q=(self.request.query_params.get("q") or self.request.query_params.get("search") or "").strip(),
        ).order_by("nombre")
