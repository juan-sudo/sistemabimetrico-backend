from apps.personal.models.personal import Personal
from apps.reporte_asistencia_diaria.models import ReporteAsistenciaDiaria
from apps.reporte_concepto_personal.models import ReporteConceptoPersonal
from apps.reporte_incidencia_personal.models import ReporteIncidenciaPersonal
from apps.reporte_personal_mensual.models import ReportePersonalMensual


def get_personal_reporte_base_queryset():
    return Personal.objects.select_related(
        "empresa",
        "sucursal",
        "area",
        "tipo_documento",
        "tipo_trabajador",
        "categoria",
        "cargo",
    ).all()


def get_reporte_personal_queryset():
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


def get_reporte_asistencia_queryset():
    return ReporteAsistenciaDiaria.objects.select_related(
        "reporte",
        "reporte__personal",
        "reporte__personal__empresa",
        "reporte__personal__sucursal",
        "reporte__personal__area",
    ).all()


def get_reporte_conceptos_queryset():
    return ReporteConceptoPersonal.objects.select_related(
        "reporte",
        "reporte__personal",
        "reporte__personal__empresa",
        "reporte__personal__sucursal",
        "reporte__personal__area",
    ).all()


def get_reporte_incidencias_queryset():
    return ReporteIncidenciaPersonal.objects.select_related(
        "reporte",
        "reporte__personal",
        "reporte__personal__empresa",
        "reporte__personal__sucursal",
        "reporte__personal__area",
    ).all()


__all__ = [
    "get_personal_reporte_base_queryset",
    "get_reporte_asistencia_queryset",
    "get_reporte_conceptos_queryset",
    "get_reporte_incidencias_queryset",
    "get_reporte_personal_queryset",
]
