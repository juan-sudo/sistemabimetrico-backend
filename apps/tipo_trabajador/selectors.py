from django.db import models

from apps.tipo_trabajador.models import TipoTrabajador


def get_tipo_trabajador_queryset():
    return TipoTrabajador.objects.all()


def filter_tipo_trabajador_queryset(queryset, *, activo=None, q=None):
    if activo not in (None, ""):
        normalized = str(activo).strip().lower()
        if normalized in {"true", "1", "si", "sí", "activo"}:
            queryset = queryset.filter(activo=True)
        elif normalized in {"false", "0", "no", "inactivo"}:
            queryset = queryset.filter(activo=False)
    if q:
        queryset = queryset.filter(
            models.Q(codigo__icontains=q)
            | models.Q(descripcion__icontains=q)
        )
    return queryset


__all__ = ["filter_tipo_trabajador_queryset", "get_tipo_trabajador_queryset"]
