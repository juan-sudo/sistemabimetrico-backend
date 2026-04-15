from django.contrib.auth import get_user_model

from apps.usuario.models import UsuarioModuloPermiso

User = get_user_model()

__all__ = ["User", "UsuarioModuloPermiso"]
