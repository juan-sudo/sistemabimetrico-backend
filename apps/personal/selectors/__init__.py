from django.db import models

from apps.personal.models.personal import Personal


def get_personal_queryset():
    return Personal.objects.select_related(
        "empresa",
        "sucursal",
        "area",
        "ubicacion",
        "tipo_documento",
        "tipo_trabajador",
        "categoria",
        "tipo_sindicato",
        "cargo",
    ).all()


def filter_personal_queryset(queryset, *, empresa=None, sucursal=None, area=None, estado=None, q=None):
    if empresa:
        queryset = queryset.filter(empresa_id=empresa)
    if sucursal:
        queryset = queryset.filter(sucursal_id=sucursal)
    if area:
        queryset = queryset.filter(area_id=area)
    if estado:
        queryset = queryset.filter(estado=estado)
    if q:
        queryset = queryset.filter(
            models.Q(nombres_completos__icontains=q)
            | models.Q(numero_documento__icontains=q)
            | models.Q(codigo_empleado__icontains=q)
            | models.Q(correo__icontains=q)
            | models.Q(telefono__icontains=q)
            | models.Q(area__nombre__icontains=q)
            | models.Q(sucursal__nombre__icontains=q)
            | models.Q(empresa__razon_social__icontains=q)
        )
    return queryset


__all__ = ["filter_personal_queryset", "get_personal_queryset"]
