from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination

from apps.core.api import BaseModelViewSet
from apps.empresa.models import Empresa
from apps.empresa.serializers import EmpresaListSerializer, EmpresaSerializer


class EmpresaPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class EmpresaViewSet(BaseModelViewSet):
    queryset = Empresa.objects.only(
        "id",
        "codigo",
        "razon_social",
        "ruc",
        "correo",
        "logo",
        "activo",
        "created_at",
        "updated_at",
    ).order_by("razon_social")
    serializer_class = EmpresaSerializer
    pagination_class = EmpresaPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["codigo", "razon_social", "ruc", "correo"]
    ordering_fields = ["codigo", "razon_social", "ruc", "created_at", "updated_at"]
    ordering = ["razon_social"]

    def get_serializer_class(self):
        if self.action == "list":
            return EmpresaListSerializer
        return EmpresaSerializer
