from django.db import models

from apps.sucursal.models import Sucursal


def get_sucursal_queryset():
    return Sucursal.objects.select_related("empresa").all()


def filter_sucursal_queryset(queryset, *, empresa=None, activo=None, q=None):
    if empresa:
        queryset = queryset.filter(empresa_id=empresa)
    if activo not in (None, ""):
        normalized = str(activo).strip().lower()
        if normalized in {"true", "1", "si", "sí", "activo"}:
            queryset = queryset.filter(activo=True)
        elif normalized in {"false", "0", "no", "inactivo"}:
            queryset = queryset.filter(activo=False)
    if q:
        queryset = queryset.filter(
            models.Q(codigo__icontains=q)
            | models.Q(nombre__icontains=q)
            | models.Q(empresa__razon_social__icontains=q)
            | models.Q(empresa__codigo__icontains=q)
        )
    return queryset


__all__ = ["filter_sucursal_queryset", "get_sucursal_queryset"]
