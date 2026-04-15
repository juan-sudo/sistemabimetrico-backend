from apps.core.api import BaseModelViewSet
from apps.tipo_trabajador.models import TipoTrabajador
from apps.tipo_trabajador.selectors import filter_tipo_trabajador_queryset, get_tipo_trabajador_queryset
from apps.tipo_trabajador.serializers import TipoTrabajadorSerializer


class TipoTrabajadorViewSet(BaseModelViewSet):
    queryset = TipoTrabajador.objects.all()
    serializer_class = TipoTrabajadorSerializer

    def get_queryset(self):
        queryset = get_tipo_trabajador_queryset()
        return filter_tipo_trabajador_queryset(
            queryset,
            activo=self.request.query_params.get("activo"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("descripcion")
