from django.contrib.auth import get_user_model

from apps.core.api import BaseModelViewSet
from apps.usuario.selectors import filter_usuario_queryset, get_usuario_queryset
from apps.usuario.serializers import UserSerializer


User = get_user_model()


class UsuarioViewSet(BaseModelViewSet):
    queryset = User.objects.prefetch_related("module_permissions").all().order_by("username")
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = get_usuario_queryset()
        return filter_usuario_queryset(
            queryset,
            activo=self.request.query_params.get("activo"),
            rol=self.request.query_params.get("rol"),
            q=(self.request.query_params.get("q") or "").strip(),
        ).order_by("username")
