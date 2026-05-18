from rest_framework.pagination import PageNumberPagination

from apps.core.api import BaseModelViewSet
from apps.tipo_sindicato.models import TipoSindicato
from apps.tipo_sindicato.selectors import filter_tipo_sindicato_queryset, get_tipo_sindicato_queryset
from apps.tipo_sindicato.serializers import TipoSindicatoSerializer


class TipoSindicatoPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class TipoSindicatoViewSet(BaseModelViewSet):
    queryset = TipoSindicato.objects.only("id", "codigo", "descripcion", "activo")
    serializer_class = TipoSindicatoSerializer
    pagination_class = TipoSindicatoPagination

    def get_queryset(self):
        queryset = get_tipo_sindicato_queryset()
        return filter_tipo_sindicato_queryset(
            queryset,
            activo=self.request.query_params.get("activo"),
            q=(self.request.query_params.get("q") or self.request.query_params.get("search") or "").strip(),
        ).order_by("descripcion")
