from rest_framework.pagination import PageNumberPagination

from apps.core.api import BaseModelViewSet
from apps.tipo_trabajador.models import TipoTrabajador
from apps.tipo_trabajador.selectors import filter_tipo_trabajador_queryset, get_tipo_trabajador_queryset
from apps.tipo_trabajador.serializers import TipoTrabajadorSerializer


class TipoTrabajadorPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class TipoTrabajadorViewSet(BaseModelViewSet):
    queryset = TipoTrabajador.objects.only("id", "codigo", "descripcion", "activo")
    serializer_class = TipoTrabajadorSerializer
    pagination_class = TipoTrabajadorPagination

    def get_queryset(self):
        queryset = get_tipo_trabajador_queryset()
        return filter_tipo_trabajador_queryset(
            queryset,
            activo=self.request.query_params.get("activo"),
            q=(self.request.query_params.get("q") or self.request.query_params.get("search") or "").strip(),
        ).order_by("descripcion")
