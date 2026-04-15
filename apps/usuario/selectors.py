from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


def get_usuario_queryset():
    return User.objects.prefetch_related("module_permissions").all()


def filter_usuario_queryset(queryset, *, activo=None, rol=None, q=None):
    if activo not in (None, ""):
        normalized = str(activo).strip().lower()
        if normalized in {"true", "1", "si", "sí", "activo"}:
            queryset = queryset.filter(is_active=True)
        elif normalized in {"false", "0", "no", "inactivo"}:
            queryset = queryset.filter(is_active=False)
    if rol:
        normalized_role = str(rol).strip().upper()
        if normalized_role == "ADMINISTRADOR":
            queryset = queryset.filter(models.Q(is_staff=True) | models.Q(is_superuser=True))
        elif normalized_role == "USUARIO":
            queryset = queryset.filter(is_staff=False, is_superuser=False)
    if q:
        queryset = queryset.filter(
            models.Q(username__icontains=q)
            | models.Q(email__icontains=q)
            | models.Q(first_name__icontains=q)
            | models.Q(last_name__icontains=q)
        )
    return queryset


__all__ = ["filter_usuario_queryset", "get_usuario_queryset"]
