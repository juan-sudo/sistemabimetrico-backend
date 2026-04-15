from datetime import datetime

from django.db import transaction
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


class DescargaMarcacionViewSet(BaseModelViewSet):
    queryset = DescargaMarcacion.objects.all()
    serializer_class = DescargaMarcacionSerializer

    @action(detail=False, methods=["get"], url_path="notificaciones-faltantes")
    def notificaciones_faltantes(self, request):
        return Response(build_missing_mark_notifications())

    @action(detail=False, methods=["post"], url_path="ver-capacidad-dispositivo")
    def ver_capacidad_dispositivo(self, request):
        raw_ids = request.data.get("dispositivo_ids") or []
        try:
            device_ids = [int(item) for item in raw_ids]
        except (TypeError, ValueError):
            return Response({"detail": "dispositivo_ids debe ser una lista de enteros."}, status=status.HTTP_400_BAD_REQUEST)

        if not device_ids:
            return Response({"detail": "Selecciona al menos un dispositivo."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            password = int(request.data.get("clave_comunicacion") or 0)
        except (TypeError, ValueError):
            return Response({"detail": "La clave de comunicacion debe ser numerica."}, status=status.HTTP_400_BAD_REQUEST)

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response({"detail": "No se encontraron dispositivos activos para leer."}, status=status.HTTP_400_BAD_REQUEST)

        resultados = []
        for dispositivo in dispositivos:
            try:
                capacidad = read_device_capacity(host=dispositivo.direccion, port=dispositivo.puerto, password=password)
                resultados.append({"dispositivo_id": dispositivo.id, "dispositivo": dispositivo.nombre, "estado": "ok", "detalle": "Capacidad leida en modo solo lectura.", **capacidad})
            except BiometricConnectionError as exc:
                resultados.append({"dispositivo_id": dispositivo.id, "dispositivo": dispositivo.nombre, "estado": "error", "detalle": str(exc)})

        return Response({"procesados": len(dispositivos), "resultados": resultados})

    @action(detail=False, methods=["post"], url_path="ver-raw-dispositivo")
    def ver_raw_dispositivo(self, request):
        raw_ids = request.data.get("dispositivo_ids") or []
        try:
            device_ids = [int(item) for item in raw_ids]
        except (TypeError, ValueError):
            return Response({"detail": "dispositivo_ids debe ser una lista de enteros."}, status=status.HTTP_400_BAD_REQUEST)

        if not device_ids:
            return Response({"detail": "Selecciona al menos un dispositivo."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            password = int(request.data.get("clave_comunicacion") or 0)
        except (TypeError, ValueError):
            return Response({"detail": "La clave de comunicacion debe ser numerica."}, status=status.HTTP_400_BAD_REQUEST)

        fecha_inicio_raw = request.data.get("fecha_inicio")
        fecha_fin_raw = request.data.get("fecha_fin")
        fecha_inicio = None
        fecha_fin = None
        if fecha_inicio_raw:
            try:
                fecha_inicio = datetime.strptime(str(fecha_inicio_raw), "%Y-%m-%d").date()
            except ValueError:
                return Response({"detail": "fecha_inicio debe tener formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        if fecha_fin_raw:
            try:
                fecha_fin = datetime.strptime(str(fecha_fin_raw), "%Y-%m-%d").date()
            except ValueError:
                return Response({"detail": "fecha_fin debe tener formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if fecha_inicio and not fecha_fin:
            fecha_fin = fecha_inicio
        if fecha_fin and not fecha_inicio:
            fecha_inicio = fecha_fin
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            return Response({"detail": "fecha_inicio no puede ser mayor que fecha_fin."}, status=status.HTTP_400_BAD_REQUEST)

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response({"detail": "No se encontraron dispositivos activos para leer."}, status=status.HTTP_400_BAD_REQUEST)

        personal_por_codigo = {str(item.codigo_empleado).strip(): item for item in Personal.objects.exclude(codigo_empleado="")}
        personal_por_documento = {str(item.numero_documento).strip(): item for item in Personal.objects.exclude(numero_documento="")}

        resultados = []
        raw_logs = []
        for dispositivo in dispositivos:
            try:
                logs = read_attendance_logs(host=dispositivo.direccion, port=dispositivo.puerto, password=password)
            except BiometricConnectionError as exc:
                resultados.append({"dispositivo_id": dispositivo.id, "dispositivo": dispositivo.nombre, "estado": "error", "detalle": str(exc), "leidos": 0, "vinculados": 0, "sin_personal": 0})
                continue

            logs_filtrados = []
            for log in logs:
                log_date = log.timestamp.date()
                if fecha_inicio and log_date < fecha_inicio:
                    continue
                if fecha_fin and log_date > fecha_fin:
                    continue
                logs_filtrados.append(log)

            vinculados = 0
            sin_personal = 0
            for log in logs_filtrados:
                personal = personal_por_codigo.get(log.user_code) or personal_por_documento.get(log.user_code)
                estado = "SIN_PERSONAL"
                personal_id = None
                personal_documento = ""
                personal_nombre = ""
                if personal is not None:
                    estado = "VINCULADO"
                    personal_id = personal.id
                    personal_documento = personal.numero_documento
                    personal_nombre = personal.nombres_completos
                    vinculados += 1
                else:
                    sin_personal += 1

                raw_logs.append({
                    "dispositivo_id": dispositivo.id,
                    "dispositivo": dispositivo.nombre,
                    "user_code": log.user_code,
                    "timestamp": log.timestamp,
                    "punch": log.punch,
                    "tipo_evento": (Marcacion.TipoEvento.SALIDA if log.punch in {1, 5} else Marcacion.TipoEvento.ENTRADA),
                    "estado": estado,
                    "personal_id": personal_id,
                    "personal_documento": personal_documento,
                    "personal_nombre": personal_nombre,
                    "equipo_nombre": log.device_user_name,
                    "equipo_raw": log.raw_data or {},
                })

            resultados.append({"dispositivo_id": dispositivo.id, "dispositivo": dispositivo.nombre, "estado": "ok", "detalle": "Lectura RAW en modo solo lectura. No se guardo en base de datos.", "leidos_equipo": len(logs), "leidos": len(logs_filtrados), "vinculados": vinculados, "sin_personal": sin_personal})

        return Response({"procesados": len(dispositivos), "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None, "fecha_fin": fecha_fin.isoformat() if fecha_fin else None, "resultados": resultados, "raw_logs_total": len(raw_logs), "raw_logs": raw_logs})

    @action(detail=False, methods=["post"], url_path="descargar-dispositivo")
    def descargar_dispositivo(self, request):
        raw_ids = request.data.get("dispositivo_ids") or []
        try:
            device_ids = [int(item) for item in raw_ids]
        except (TypeError, ValueError):
            return Response({"detail": "dispositivo_ids debe ser una lista de enteros."}, status=status.HTTP_400_BAD_REQUEST)

        if not device_ids:
            return Response({"detail": "Selecciona al menos un dispositivo."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            password = int(request.data.get("clave_comunicacion") or 0)
        except (TypeError, ValueError):
            return Response({"detail": "La clave de comunicacion debe ser numerica."}, status=status.HTTP_400_BAD_REQUEST)

        dispositivos = list(Dispositivo.objects.filter(id__in=device_ids, activo=True))
        if not dispositivos:
            return Response({"detail": "No se encontraron dispositivos activos para descargar."}, status=status.HTTP_400_BAD_REQUEST)

        resultados = []
        total_creadas = 0
        total_duplicadas = 0
        raw_logs = []
        periodos_a_sincronizar = set()
        personal_a_sincronizar = {}

        for dispositivo in dispositivos:
            try:
                logs = read_attendance_logs(host=dispositivo.direccion, port=dispositivo.puerto, password=password)
            except BiometricConnectionError as exc:
                resultados.append({"dispositivo_id": dispositivo.id, "dispositivo": dispositivo.nombre, "creadas": 0, "duplicadas": 0, "sin_personal": 0, "estado": "error", "detalle": str(exc)})
                continue

            personal_por_codigo = {str(item.codigo_empleado).strip(): item for item in Personal.objects.exclude(codigo_empleado="")}
            personal_por_documento = {str(item.numero_documento).strip(): item for item in Personal.objects.exclude(numero_documento="")}

            creadas = 0
            duplicadas = 0
            sin_personal = 0

            with transaction.atomic():
                descarga = DescargaMarcacion.objects.create(dispositivo=dispositivo, fuente=DescargaMarcacion.Fuente.DISPOSITIVO, ejecutado_por=request.user, observacion="Descarga en modo solo lectura desde dispositivo biometrico.")

                for log in logs:
                    personal = personal_por_codigo.get(log.user_code) or personal_por_documento.get(log.user_code)
                    if personal is None:
                        raw_logs.append({
                            "dispositivo_id": dispositivo.id,
                            "dispositivo": dispositivo.nombre,
                            "user_code": log.user_code,
                            "timestamp": log.timestamp,
                            "punch": log.punch,
                            "tipo_evento": (Marcacion.TipoEvento.SALIDA if log.punch in {1, 5} else Marcacion.TipoEvento.ENTRADA),
                            "estado": "SIN_PERSONAL",
                            "personal_id": None,
                            "personal_documento": "",
                            "personal_nombre": "",
                            "equipo_nombre": log.device_user_name,
                            "equipo_raw": log.raw_data or {},
                        })
                        sin_personal += 1
                        continue

                    tipo_evento = Marcacion.TipoEvento.SALIDA if log.punch in {1, 5} else Marcacion.TipoEvento.ENTRADA
                    _, created = Marcacion.objects.get_or_create(
                        personal=personal,
                        fecha_hora=log.timestamp,
                        defaults={
                            "dispositivo": dispositivo,
                            "descarga": descarga,
                            "codigo_equipo": log.user_code,
                            "tipo_evento": tipo_evento,
                            "situacion": Marcacion.Situacion.ACTIVO,
                        },
                    )
                    if created:
                        creadas += 1
                        raw_logs.append({
                            "dispositivo_id": dispositivo.id,
                            "dispositivo": dispositivo.nombre,
                            "user_code": log.user_code,
                            "timestamp": log.timestamp,
                            "punch": log.punch,
                            "tipo_evento": tipo_evento,
                            "estado": "CREADA",
                            "personal_id": personal.id,
                            "personal_documento": personal.numero_documento,
                            "personal_nombre": personal.nombres_completos,
                            "equipo_nombre": log.device_user_name,
                            "equipo_raw": log.raw_data or {},
                        })
                        periodos_a_sincronizar.add((personal.id, log.timestamp.year, log.timestamp.month))
                        personal_a_sincronizar[personal.id] = personal
                    else:
                        duplicadas += 1
                        raw_logs.append({
                            "dispositivo_id": dispositivo.id,
                            "dispositivo": dispositivo.nombre,
                            "user_code": log.user_code,
                            "timestamp": log.timestamp,
                            "punch": log.punch,
                            "tipo_evento": tipo_evento,
                            "estado": "DUPLICADA",
                            "personal_id": personal.id,
                            "personal_documento": personal.numero_documento,
                            "personal_nombre": personal.nombres_completos,
                            "equipo_nombre": log.device_user_name,
                            "equipo_raw": log.raw_data or {},
                        })

                if creadas == 0 and duplicadas == 0 and sin_personal == 0:
                    descarga.observacion = "Descarga ejecutada sin marcaciones."
                elif creadas == 0 and duplicadas > 0 and sin_personal == 0:
                    descarga.observacion = "Descarga ejecutada. Todas las marcaciones ya existian."
                elif sin_personal > 0:
                    descarga.observacion = f"Descarga ejecutada. {sin_personal} marcaciones sin personal asociado."
                descarga.save(update_fields=["observacion"])

            total_creadas += creadas
            total_duplicadas += duplicadas
            resultados.append({"dispositivo_id": dispositivo.id, "dispositivo": dispositivo.nombre, "creadas": creadas, "duplicadas": duplicadas, "sin_personal": sin_personal, "estado": "ok", "detalle": "Lectura completada sin escribir en el reloj."})

        reportes_actualizados = 0
        for personal_id, anio, mes in sorted(periodos_a_sincronizar, key=lambda item: (item[1], item[2], item[0])):
            personal = personal_a_sincronizar.get(personal_id)
            if personal is None:
                continue
            sync_reporte_general(personal, anio, mes)
            reportes_actualizados += 1

        return Response({"procesados": len(dispositivos), "total_creadas": total_creadas, "total_duplicadas": total_duplicadas, "reportes_actualizados": reportes_actualizados, "resultados": resultados, "raw_logs_total": len(raw_logs), "raw_logs": raw_logs, "notificaciones": build_missing_mark_notifications()})
