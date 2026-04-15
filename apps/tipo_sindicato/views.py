from apps.core.api import BaseModelViewSet
from apps.tipo_sindicato.models import TipoSindicato
from apps.tipo_sindicato.selectors import filter_tipo_sindicato_queryset, get_tipo_sindicato_queryset
from apps.tipo_sindicato.serializers import TipoSindicatoSerializer


class TipoSindicatoViewSet(BaseModelViewSet):
    queryset = TipoSindicato.objects.all()
    serializer_class = TipoSindicatoSerializer

    def get_queryset(self):
        queryset = get_tipo_sindicato_queryset()
        return filter_tipo_sindicato_queryset(
            queryset,
            activo=self.request.query_params.get("activo"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("descripcion")
