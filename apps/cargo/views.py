from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from apps.cargo.models import Cargo
from apps.cargo.serializers import CargoSerializer
from apps.core.api import BaseModelViewSet


class CargoPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class CargoViewSet(BaseModelViewSet):
    queryset = Cargo.objects.only("id", "codigo", "descripcion", "activo").order_by("descripcion")
    serializer_class = CargoSerializer
    pagination_class = CargoPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        q = (self.request.query_params.get("q") or self.request.query_params.get("search") or "").strip()
        activo = (self.request.query_params.get("activo") or "").strip().lower()

        if activo in {"1", "true", "si", "sí", "activo"}:
            queryset = queryset.filter(activo=True)
        elif activo in {"0", "false", "no", "inactivo"}:
            queryset = queryset.filter(activo=False)

        if q:
            queryset = queryset.filter(
                Q(codigo__icontains=q)
                | Q(descripcion__icontains=q)
            )

        return queryset
