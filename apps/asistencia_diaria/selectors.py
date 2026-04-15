from apps.reporte_asistencia_diaria.selectors import (
    filter_reporte_asistencia_diaria_queryset,
    get_reporte_asistencia_diaria_queryset,
)


def get_asistencia_diaria_queryset():
    return get_reporte_asistencia_diaria_queryset()


def filter_asistencia_diaria_queryset(
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
    return filter_reporte_asistencia_diaria_queryset(
        queryset,
        reporte=reporte,
        personal=personal,
        anio=anio,
        mes=mes,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado_dia=estado_dia,
    )


__all__ = [
    "filter_asistencia_diaria_queryset",
    "get_asistencia_diaria_queryset",
]
