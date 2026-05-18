from datetime import datetime

from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.conexion_equipo_biometrico.services import BiometricConnectionError, read_attendance_logs, read_device_capacity
from apps.conexion_equipo_biometrico.services.notifications import build_missing_mark_notifications
from apps.core.api import BaseModelViewSet
from apps.descarga_marcacion.models import DescargaMarcacion
from apps.descarga_marcacion.serializers import DescargaMarcacionSerializer
from apps.marcacion.models import Marcacion
from apps.personal.models.dispositivo import Dispositivo
from apps.personal.models.personal import Personal
from apps.reportes.services import sync_reporte_general

try:
    from apps.reportes.tasks import task_sync_reporte_general
except Exception:  # pragma: no cover - optional dependency
    task_sync_reporte_general = None

MAX_RAW_LIMIT = 5000
DEFAULT_RAW_LIMIT = 500
LOG_BATCH_SIZE = 2000
INSERT_BATCH_SIZE = 1000


def _parse_device_ids(request):
    raw_ids = request.data.get("dispositivo_ids") or []
    try:
        device_ids = [int(item) for item in raw_ids]
    except (TypeError, ValueError):
        return None, Response({"detail": "dispositivo_ids debe ser una lista de enteros."}, status=status.HTTP_400_BAD_REQUEST)

    if not device_ids:
        return None, Response({"detail": "Selecciona al menos un dispositivo."}, status=status.HTTP_400_BAD_REQUEST)

    return device_ids, None


def _parse_password(request):
    try:
        return int(request.data.get("clave_comunicacion") or 0), None
    except (TypeError, ValueError):
        return None, Response({"detail": "La clave de comunicacion debe ser numerica."}, status=status.HTTP_400_BAD_REQUEST)


def _parse_bool(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "si", "sÃ­"}


def _parse_int(value, default_value, min_value=0, max_value=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default_value

    if parsed < min_value:
        parsed = min_value
    if max_value is not None and parsed > max_value:
        parsed = max_value
    return parsed


def _parse_raw_window(request):
    include_raw = _parse_bool(request.data.get("include_raw"))
    raw_offset = _parse_int(request.data.get("raw_offset"), 0, min_value=0)
    raw_limit = _parse_int(request.data.get("raw_limit"), DEFAULT_RAW_LIMIT, min_value=1, max_value=MAX_RAW_LIMIT)
    return include_raw, raw_offset, raw_limit


def _append_raw(raw_logs, payload, *, include_raw, raw_offset, raw_limit, raw_index):
    if not include_raw:
        return
    if raw_index < raw_offset:
        return
    relative = raw_index - raw_offset
    if relative >= raw_limit:
        return
    raw_logs.append(payload)


def _parse_date_range(request):
    fecha_inicio_raw = request.data.get("fecha_inicio")
    fecha_fin_raw = request.data.get("fecha_fin")
    fecha_inicio = None
    fecha_fin = None

    if fecha_inicio_raw:
        try:
            fecha_inicio = datetime.strptime(str(fecha_inicio_raw), "%Y-%m-%d").date()
        except ValueError:
            return None, None, Response({"detail": "fecha_inicio debe tener formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    if fecha_fin_raw:
        try:
            fecha_fin = datetime.strptime(str(fecha_fin_raw), "%Y-%m-%d").date()
        except ValueError:
            return None, None, Response({"detail": "fecha_fin debe tener formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    if fecha_inicio and not fecha_fin:
        fecha_fin = fecha_inicio
    if fecha_fin and not fecha_inicio:
        fecha_inicio = fecha_fin

    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        return None, None, Response({"detail": "fecha_inicio no puede ser mayor que fecha_fin."}, status=status.HTTP_400_BAD_REQUEST)

    return fecha_inicio, fecha_fin, None


def _sync_reportes(periodos_a_sincronizar, personal_cache):
    reportes_actualizados = 0

    if task_sync_reporte_general is not None:
        for personal_id, anio, mes in sorted(periodos_a_sincronizar, key=lambda item: (item[1], item[2], item[0])):
            try:
                task_sync_reporte_general.delay(personal_id, anio, mes)
                reportes_actualizados += 1
            except Exception:
                continue
        return reportes_actualizados

    for personal_id, anio, mes in sorted(periodos_a_sincronizar, key=lambda item: (item[1], item[2], item[0])):
        personal = personal_cache.get(personal_id)
        if personal is None:
            personal = Personal.objects.filter(pk=personal_id).first()
        if personal is None:
            continue
        try:
            sync_reporte_general(personal, anio, mes)
            reportes_actualizados += 1
        except Exception:
            continue

    return reportes_actualizados


class DescargaMarcacionViewSet(BaseModelViewSet):
    queryset = DescargaMarcacion.objects.all()
    serializer_class = DescargaMarcacionSerializer

    @action(detail=False, methods=["get"], url_path="notificaciones-faltantes")
    def notificaciones_faltantes(self, request):
        return Response(build_missing_mark_notifications())

    @action(detail=False, methods=["post"], url_path="ver-capacidad-dispositivo")
    def ver_capacidad_dispositivo(self, request):
        device_ids, error_response = _parse_device_ids(request)
        if error_response is not None:
            return error_response

        password, error_response = _parse_password(request)
        if error_response is not None:
            return error_response

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response({"detail": "No se encontraron dispositivos activos para leer."}, status=status.HTTP_400_BAD_REQUEST)

        resultados = []
        for dispositivo in dispositivos:
            try:
                capacidad = read_device_capacity(host=dispositivo.direccion, port=dispositivo.puerto, password=password)
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "estado": "ok",
                        "detalle": "Capacidad leida en modo solo lectura.",
                        **capacidad,
                    }
                )
            except BiometricConnectionError as exc:
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "estado": "error",
                        "detalle": str(exc),
                    }
                )

        return Response({"procesados": len(dispositivos), "resultados": resultados})

    @action(detail=False, methods=["post"], url_path="ver-raw-dispositivo")
    def ver_raw_dispositivo(self, request):
        device_ids, error_response = _parse_device_ids(request)
        if error_response is not None:
            return error_response

        password, error_response = _parse_password(request)
        if error_response is not None:
            return error_response

        fecha_inicio, fecha_fin, error_response = _parse_date_range(request)
        if error_response is not None:
            return error_response

        include_raw, raw_offset, raw_limit = _parse_raw_window(request)

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response({"detail": "No se encontraron dispositivos activos para leer."}, status=status.HTTP_400_BAD_REQUEST)

        personal_por_codigo = {
            str(item.codigo_empleado).strip(): item
            for item in Personal.objects.exclude(codigo_empleado="").only("id", "codigo_empleado", "numero_documento", "nombres_completos")
        }
        personal_por_documento = {
            str(item.numero_documento).strip(): item
            for item in Personal.objects.exclude(numero_documento="").only("id", "numero_documento", "nombres_completos")
        }

        resultados = []
        raw_logs = []
        raw_logs_total = 0

        for dispositivo in dispositivos:
            try:
                logs = read_attendance_logs(host=dispositivo.direccion, port=dispositivo.puerto, password=password)
            except BiometricConnectionError as exc:
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "estado": "error",
                        "detalle": str(exc),
                        "leidos": 0,
                        "vinculados": 0,
                        "sin_personal": 0,
                    }
                )
                continue

            vinculados = 0
            sin_personal = 0
            leidos_filtrados = 0

            for log in logs:
                log_date = log.timestamp.date()
                if fecha_inicio and log_date < fecha_inicio:
                    continue
                if fecha_fin and log_date > fecha_fin:
                    continue

                leidos_filtrados += 1
                personal = personal_por_codigo.get(log.user_code) or personal_por_documento.get(log.user_code)
                tipo_evento = Marcacion.TipoEvento.SALIDA if log.punch in {1, 5} else Marcacion.TipoEvento.ENTRADA

                if personal is not None:
                    vinculados += 1
                    estado = "VINCULADO"
                    personal_id = personal.id
                    personal_documento = personal.numero_documento
                    personal_nombre = personal.nombres_completos
                else:
                    sin_personal += 1
                    estado = "SIN_PERSONAL"
                    personal_id = None
                    personal_documento = ""
                    personal_nombre = ""

                _append_raw(
                    raw_logs,
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "user_code": log.user_code,
                        "timestamp": log.timestamp,
                        "punch": log.punch,
                        "tipo_evento": tipo_evento,
                        "estado": estado,
                        "personal_id": personal_id,
                        "personal_documento": personal_documento,
                        "personal_nombre": personal_nombre,
                        "equipo_nombre": log.device_user_name,
                        "equipo_raw": log.raw_data or {},
                    },
                    include_raw=include_raw,
                    raw_offset=raw_offset,
                    raw_limit=raw_limit,
                    raw_index=raw_logs_total,
                )
                raw_logs_total += 1

            resultados.append(
                {
                    "dispositivo_id": dispositivo.id,
                    "dispositivo": dispositivo.nombre,
                    "estado": "ok",
                    "detalle": "Lectura RAW en modo solo lectura. No se guardo en base de datos.",
                    "leidos_equipo": len(logs),
                    "leidos": leidos_filtrados,
                    "vinculados": vinculados,
                    "sin_personal": sin_personal,
                }
            )

        payload = {
            "procesados": len(dispositivos),
            "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
            "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
            "resultados": resultados,
            "raw_logs_total": raw_logs_total,
            "raw_logs_offset": raw_offset,
            "raw_logs_limit": raw_limit,
            "include_raw": include_raw,
        }
        if include_raw:
            payload["raw_logs"] = raw_logs
        return Response(payload)

    @action(detail=False, methods=["post"], url_path="descargar-dispositivo")
    def descargar_dispositivo(self, request):
        device_ids, error_response = _parse_device_ids(request)
        if error_response is not None:
            return error_response

        password, error_response = _parse_password(request)
        if error_response is not None:
            return error_response

        include_raw, raw_offset, raw_limit = _parse_raw_window(request)

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response({"detail": "No se encontraron dispositivos activos para descargar."}, status=status.HTTP_400_BAD_REQUEST)

        resultados = []
        total_creadas = 0
        total_duplicadas = 0
        total_sin_personal = 0
        raw_logs = []
        raw_logs_total = 0
        periodos_a_sincronizar = set()
        personal_a_sincronizar = {}

        for dispositivo in dispositivos:
            try:
                logs = read_attendance_logs(host=dispositivo.direccion, port=dispositivo.puerto, password=password)
            except BiometricConnectionError as exc:
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "creadas": 0,
                        "duplicadas": 0,
                        "sin_personal": 0,
                        "estado": "error",
                        "detalle": str(exc),
                    }
                )
                continue

            user_codes = {str(log.user_code).strip() for log in logs if log.user_code}
            if not user_codes:
                resultados.append(
                    {
                        "dispositivo_id": dispositivo.id,
                        "dispositivo": dispositivo.nombre,
                        "creadas": 0,
                        "duplicadas": 0,
                        "sin_personal": 0,
                        "estado": "ok",
                        "detalle": "El dispositivo no reporto marcaciones.",
                    }
                )
                continue

            personal_encontrado = list(
                Personal.objects.filter(Q(codigo_empleado__in=user_codes) | Q(numero_documento__in=user_codes)).only(
                    "id", "codigo_empleado", "numero_documento", "nombres_completos"
                )
            )
            personal_por_codigo = {str(p.codigo_empleado).strip(): p for p in personal_encontrado if p.codigo_empleado}
            personal_por_documento = {str(p.numero_documento).strip(): p for p in personal_encontrado if p.numero_documento}

            creadas = 0
            duplicadas = 0
            sin_personal = 0
            marcaciones_buffer = []
            seen_new_pairs = set()

            with transaction.atomic():
                descarga = DescargaMarcacion.objects.create(
                    dispositivo=dispositivo,
                    fuente=DescargaMarcacion.Fuente.DISPOSITIVO,
                    ejecutado_por=request.user,
                    observacion="Descarga en modo solo lectura desde dispositivo biometrico.",
                )

                for batch_start in range(0, len(logs), LOG_BATCH_SIZE):
                    batch_logs = logs[batch_start : batch_start + LOG_BATCH_SIZE]
                    resolved = []

                    for log in batch_logs:
                        user_code_stripped = str(log.user_code).strip()
                        personal = personal_por_codigo.get(user_code_stripped) or personal_por_documento.get(user_code_stripped)
                        tipo_evento = Marcacion.TipoEvento.SALIDA if log.punch in {1, 5} else Marcacion.TipoEvento.ENTRADA

                        if personal is None:
                            sin_personal += 1
                            _append_raw(
                                raw_logs,
                                {
                                    "dispositivo_id": dispositivo.id,
                                    "dispositivo": dispositivo.nombre,
                                    "user_code": log.user_code,
                                    "timestamp": log.timestamp,
                                    "punch": log.punch,
                                    "tipo_evento": tipo_evento,
                                    "estado": "SIN_PERSONAL",
                                    "personal_id": None,
                                    "personal_documento": "",
                                    "personal_nombre": "",
                                    "equipo_nombre": log.device_user_name,
                                    "equipo_raw": log.raw_data or {},
                                },
                                include_raw=include_raw,
                                raw_offset=raw_offset,
                                raw_limit=raw_limit,
                                raw_index=raw_logs_total,
                            )
                            raw_logs_total += 1
                            continue

                        resolved.append((personal, log, tipo_evento))

                    if not resolved:
                        continue

                    personal_ids = {item[0].id for item in resolved}
                    timestamps = {item[1].timestamp for item in resolved}
                    existentes = set(
                        Marcacion.objects.filter(personal_id__in=personal_ids, fecha_hora__in=timestamps).values_list("personal_id", "fecha_hora")
                    )

                    for personal, log, tipo_evento in resolved:
                        key = (personal.id, log.timestamp)
                        es_duplicado = key in existentes or key in seen_new_pairs

                        if es_duplicado:
                            duplicadas += 1
                        else:
                            marcaciones_buffer.append(
                                Marcacion(
                                    personal=personal,
                                    fecha_hora=log.timestamp,
                                    dispositivo=dispositivo,
                                    descarga=descarga,
                                    codigo_equipo=log.user_code,
                                    tipo_evento=tipo_evento,
                                    situacion=Marcacion.Situacion.ACTIVO,
                                )
                            )
                            seen_new_pairs.add(key)
                            periodos_a_sincronizar.add((personal.id, log.timestamp.year, log.timestamp.month))
                            personal_a_sincronizar[personal.id] = personal
                            creadas += 1

                        _append_raw(
                            raw_logs,
                            {
                                "dispositivo_id": dispositivo.id,
                                "dispositivo": dispositivo.nombre,
                                "user_code": log.user_code,
                                "timestamp": log.timestamp,
                                "punch": log.punch,
                                "tipo_evento": tipo_evento,
                                "estado": "DUPLICADA" if es_duplicado else "CREADA",
                                "personal_id": personal.id,
                                "personal_documento": personal.numero_documento,
                                "personal_nombre": personal.nombres_completos,
                                "equipo_nombre": log.device_user_name,
                                "equipo_raw": log.raw_data or {},
                            },
                            include_raw=include_raw,
                            raw_offset=raw_offset,
                            raw_limit=raw_limit,
                            raw_index=raw_logs_total,
                        )
                        raw_logs_total += 1

                        if len(marcaciones_buffer) >= INSERT_BATCH_SIZE:
                            Marcacion.objects.bulk_create(marcaciones_buffer)
                            marcaciones_buffer = []

                if marcaciones_buffer:
                    Marcacion.objects.bulk_create(marcaciones_buffer)

                if creadas == 0 and duplicadas == 0 and sin_personal == 0:
                    descarga.observacion = "Descarga ejecutada sin marcaciones."
                elif creadas == 0 and duplicadas > 0 and sin_personal == 0:
                    descarga.observacion = "Descarga ejecutada. Todas las marcaciones ya existian."
                elif sin_personal > 0:
                    descarga.observacion = f"Descarga ejecutada. {sin_personal} marcaciones sin personal asociado."
                descarga.save(update_fields=["observacion"])

            total_creadas += creadas
            total_duplicadas += duplicadas
            total_sin_personal += sin_personal

            resultados.append(
                {
                    "dispositivo_id": dispositivo.id,
                    "dispositivo": dispositivo.nombre,
                    "creadas": creadas,
                    "duplicadas": duplicadas,
                    "sin_personal": sin_personal,
                    "estado": "ok",
                    "detalle": "Lectura completada sin escribir en el reloj.",
                }
            )

        reportes_actualizados = _sync_reportes(periodos_a_sincronizar, personal_a_sincronizar)

        payload = {
            "procesados": len(dispositivos),
            "total_creadas": total_creadas,
            "total_duplicadas": total_duplicadas,
            "total_sin_personal": total_sin_personal,
            "reportes_actualizados": reportes_actualizados,
            "resultados": resultados,
            "raw_logs_total": raw_logs_total,
            "raw_logs_offset": raw_offset,
            "raw_logs_limit": raw_limit,
            "include_raw": include_raw,
            "notificaciones": build_missing_mark_notifications(),
        }
        if include_raw:
            payload["raw_logs"] = raw_logs
        return Response(payload)
