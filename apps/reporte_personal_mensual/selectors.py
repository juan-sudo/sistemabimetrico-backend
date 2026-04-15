from django.db import models

from apps.reporte_personal_mensual.models import ReportePersonalMensual


def get_reporte_personal_mensual_queryset():
    return ReportePersonalMensual.objects.select_related(
        "personal",
        "personal__empresa",
        "personal__sucursal",
        "personal__area",
        "personal__tipo_documento",
        "personal__tipo_trabajador",
        "personal__categoria",
        "personal__cargo",
    ).all()


def filter_reporte_personal_mensual_queryset(
    queryset,
    *,
    personal=None,
    empresa=None,
    sucursal=None,
    area=None,
    anio=None,
    mes=None,
    estado=None,
    q=None,
):
    if personal:
        queryset = queryset.filter(personal_id=personal)
    if empresa:
        queryset = queryset.filter(personal__empresa_id=empresa)
    if sucursal:
        queryset = queryset.filter(personal__sucursal_id=sucursal)
    if area:
        queryset = queryset.filter(personal__area_id=area)
    if anio:
        queryset = queryset.filter(anio=anio)
    if mes:
        queryset = queryset.filter(mes=mes)
    if estado:
        queryset = queryset.filter(estado=estado)
    if q:
        queryset = queryset.filter(
            models.Q(personal__codigo_empleado__icontains=q)
            | models.Q(personal__numero_documento__icontains=q)
            | models.Q(personal__nombres_completos__icontains=q)
            | models.Q(personal__empresa__razon_social__icontains=q)
            | models.Q(personal__sucursal__nombre__icontains=q)
            | models.Q(personal__area__nombre__icontains=q)
            | models.Q(observacion__icontains=q)
        )
    return queryset


__all__ = [
    "filter_reporte_personal_mensual_queryset",
    "get_reporte_personal_mensual_queryset",
]
