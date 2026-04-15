from apps.reporte_asistencia_diaria.models import ReporteAsistenciaDiaria


def get_reporte_asistencia_diaria_queryset():
    return ReporteAsistenciaDiaria.objects.select_related(
        "reporte",
        "reporte__personal",
        "reporte__personal__empresa",
        "reporte__personal__sucursal",
        "reporte__personal__area",
    ).all()


def filter_reporte_asistencia_diaria_queryset(
    queryset,
    *,
    reporte=None,
    personal=None,
    anio=None,
    mes=None,
    fecha_inicio=None,
    fecha_fin=None,
    estado_dia=None,
):
    if reporte:
        queryset = queryset.filter(reporte_id=reporte)
    if personal:
        queryset = queryset.filter(reporte__personal_id=personal)
    if anio:
        queryset = queryset.filter(reporte__anio=anio)
    if mes:
        queryset = queryset.filter(reporte__mes=mes)
    if fecha_inicio:
        queryset = queryset.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha__lte=fecha_fin)
    if estado_dia:
        queryset = queryset.filter(estado_dia=estado_dia)
    return queryset


__all__ = [
    "filter_reporte_asistencia_diaria_queryset",
    "get_reporte_asistencia_diaria_queryset",
]
