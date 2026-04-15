from django.db import models

from apps.reporte_incidencia_personal.models import ReporteIncidenciaPersonal


def get_reporte_incidencia_personal_queryset():
    return ReporteIncidenciaPersonal.objects.select_related(
        "reporte",
        "reporte__personal",
        "reporte__personal__empresa",
        "reporte__personal__sucursal",
        "reporte__personal__area",
    ).all()


def filter_reporte_incidencia_personal_queryset(
    queryset,
    *,
    reporte=None,
    personal=None,
    anio=None,
    mes=None,
    tipo=None,
    fecha_inicio=None,
    fecha_fin=None,
    q=None,
):
    if reporte:
        queryset = queryset.filter(reporte_id=reporte)
    if personal:
        queryset = queryset.filter(reporte__personal_id=personal)
    if anio:
        queryset = queryset.filter(reporte__anio=anio)
    if mes:
        queryset = queryset.filter(reporte__mes=mes)
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    if fecha_inicio:
        queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_fin__lte=fecha_fin)
    if q:
        queryset = queryset.filter(
            models.Q(descripcion__icontains=q)
            | models.Q(observacion__icontains=q)
            | models.Q(referencia_modelo__icontains=q)
            | models.Q(reporte__personal__codigo_empleado__icontains=q)
            | models.Q(reporte__personal__numero_documento__icontains=q)
            | models.Q(reporte__personal__nombres_completos__icontains=q)
        )
    return queryset


__all__ = [
    "filter_reporte_incidencia_personal_queryset",
    "get_reporte_incidencia_personal_queryset",
]
