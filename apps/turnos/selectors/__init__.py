from django.db import models

from apps.turnos.models.personal_turno import PersonalTurno
from apps.turnos.models.turno import Turno
from apps.turnos.models.turno_bloque_horario import TurnoBloqueHorario


def get_turno_queryset():
    return Turno.objects.prefetch_related("bloques").all()


def filter_turno_queryset(queryset, *, activo=None, tipo=None, q=None):
    if activo not in (None, ""):
        normalized = str(activo).strip().lower()
        if normalized in {"true", "1", "si", "sí", "activo"}:
            queryset = queryset.filter(activo=True)
        elif normalized in {"false", "0", "no", "inactivo"}:
            queryset = queryset.filter(activo=False)
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    if q:
        queryset = queryset.filter(
            models.Q(codigo__icontains=q)
            | models.Q(nombre__icontains=q)
        )
    return queryset


def get_turno_bloque_queryset():
    return TurnoBloqueHorario.objects.select_related("turno").all()


def filter_turno_bloque_queryset(queryset, *, turno=None):
    if turno:
        queryset = queryset.filter(turno_id=turno)
    return queryset


def get_personal_turno_queryset():
    return PersonalTurno.objects.select_related(
        "personal",
        "personal__sucursal",
        "personal__area",
        "turno",
    ).all()


def filter_personal_turno_queryset(queryset, *, personal=None, turno=None, fecha_inicio=None, fecha_fin=None, q=None):
    if personal:
        queryset = queryset.filter(personal_id=personal)
    if turno:
        queryset = queryset.filter(turno_id=turno)
    if fecha_inicio:
        queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__lte=fecha_fin))
    if q:
        queryset = queryset.filter(
            models.Q(personal__numero_documento__icontains=q)
            | models.Q(personal__nombres_completos__icontains=q)
            | models.Q(personal__area__nombre__icontains=q)
            | models.Q(personal__sucursal__nombre__icontains=q)
            | models.Q(turno__codigo__icontains=q)
            | models.Q(turno__nombre__icontains=q)
        )
    return queryset


__all__ = [
    "filter_personal_turno_queryset",
    "filter_turno_bloque_queryset",
    "filter_turno_queryset",
    "get_personal_turno_queryset",
    "get_turno_bloque_queryset",
    "get_turno_queryset",
]
