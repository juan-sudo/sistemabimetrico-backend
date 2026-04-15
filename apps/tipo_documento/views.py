from apps.core.api import BaseModelViewSet
from apps.tipo_documento.models import TipoDocumento
from apps.tipo_documento.selectors import filter_tipo_documento_queryset, get_tipo_documento_queryset
from apps.tipo_documento.serializers import TipoDocumentoSerializer


class TipoDocumentoViewSet(BaseModelViewSet):
    queryset = TipoDocumento.objects.all()
    serializer_class = TipoDocumentoSerializer

    def get_queryset(self):
        queryset = get_tipo_documento_queryset()
        return filter_tipo_documento_queryset(
            queryset,
            activo=self.request.query_params.get("activo"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("descripcion")
