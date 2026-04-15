from apps.core.api import BaseModelViewSet
from apps.sucursal.models import Sucursal
from apps.sucursal.selectors import filter_sucursal_queryset, get_sucursal_queryset
from apps.sucursal.serializers import SucursalSerializer


class SucursalViewSet(BaseModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer

    def get_queryset(self):
        queryset = get_sucursal_queryset()
        return filter_sucursal_queryset(
            queryset,
            empresa=self.request.query_params.get("empresa"),
            activo=self.request.query_params.get("activo"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("nombre")
