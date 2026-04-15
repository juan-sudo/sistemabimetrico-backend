from django.db import models

from apps.tipo_documento.models import TipoDocumento


def get_tipo_documento_queryset():
    return TipoDocumento.objects.all()


def filter_tipo_documento_queryset(queryset, *, activo=None, q=None):
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


__all__ = ["filter_tipo_documento_queryset", "get_tipo_documento_queryset"]
