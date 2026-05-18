from collections import defaultdict
from datetime import datetime, time, timedelta

from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView

from apps.boleta_mensual.models import BoletaMensual
from apps.descanso_medico.models import DescansoMedico
from apps.justificacion.models import Justificacion
from apps.marcacion.models import Marcacion
from apps.personal.models import Dispositivo, Personal
from apps.reportes.services import build_boleta_detalle, build_reporte_general_payload, sync_reporte_general
from apps.reporte_asistencia_diaria.api.views import ReporteAsistenciaDiariaViewSet
from apps.reporte_concepto_personal.api.views import ReporteConceptoPersonalViewSet
from apps.reporte_incidencia_personal.api.views import ReporteIncidenciaPersonalViewSet
from apps.reporte_personal_mensual.api.views import ReportePersonalMensualViewSet


class ApiRootView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Sistema"],
        summary="Raiz de la API",
        responses=inline_serializer(
            name="ApiRootResponse",
            fields={
                "name": serializers.CharField(),
                "version": serializers.CharField(),
                "health": serializers.URLField(),
                "auth_login": serializers.URLField(),
                "asistencias_diarias": serializers.URLField(),
                "reportes_personal": serializers.URLField(),
                "reportes_asistencia_diaria": serializers.URLField(),
                "reportes_conceptos": serializers.URLField(),
                "reportes_incidencias": serializers.URLField(),
            },
        ),
    )
    def get(self, request):
        return Response(
            {
                "name": "Sistema Biometrico API",
                "version": "1.0.0",
                "health": request.build_absolute_uri("health/"),
                "auth_login": request.build_absolute_uri("auth/login/"),
                "asistencias_diarias": request.build_absolute_uri("asistencias-diarias/"),
                "reportes_personal": request.build_absolute_uri("reportes-personal/"),
                "reportes_asistencia_diaria": request.build_absolute_uri("reportes-asistencia-diaria/"),
                "reportes_conceptos": request.build_absolute_uri("reportes-conceptos/"),
                "reportes_incidencias": request.build_absolute_uri("reportes-incidencias/"),
            }
        )


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Sistema"],
        summary="Health check",
        responses=inline_serializer(
            name="HealthCheckResponse",
            fields={
                "status": serializers.CharField(),
                "service": serializers.CharField(),
                "timestamp": serializers.CharField(),
            },
        ),
    )
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "backend-django",
                "timestamp": now().isoformat(),
            }
        )


class DashboardResumenView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Dashboard"],
        summary="Resumen optimizado del dashboard",
        responses=inline_serializer(
            name="DashboardResumenResponse",
            fields={
                "summary": serializers.DictField(),
                "asistencia_diaria": serializers.ListField(),
                "recent_marcaciones": serializers.ListField(),
                "recent_justificaciones": serializers.ListField(),
                "generated_at": serializers.CharField(),
            },
        ),
    )
    def get(self, request):
        today = timezone.localdate()
        month_start = today.replace(day=1)
        days = self._parse_days(request.query_params.get("days"))
        range_start = today - timedelta(days=days - 1)
        cache_key = f"dashboard-resumen:v2:{today.isoformat()}:{days}"
        cached_payload = cache.get(cache_key)
        if cached_payload:
            return Response(cached_payload)

        personal_stats = Personal.objects.aggregate(
            total=Count("id"),
            activos=Count("id", filter=Q(estado=Personal.Estado.ACTIVO)),
        )
        active_personal = personal_stats["activos"] or 0
        personal_total = personal_stats["total"] or 0
        justificaciones_stats = Justificacion.objects.aggregate(
            total=Count("id"),
            pendientes=Count("id", filter=Q(estado=Justificacion.Estado.PENDIENTE)),
        )
        justificaciones_total = justificaciones_stats["total"] or 0
        pending_justificaciones = justificaciones_stats["pendientes"] or 0

        boletas_month_stats = BoletaMensual.objects.filter(anio=today.year, mes=today.month).aggregate(
            total=Count("id"),
            neto=Sum("neto_pagar"),
        )
        boletas_month_total = boletas_month_stats["total"] or 0
        boletas_month_neto = float(boletas_month_stats["neto"] or 0)

        tz = timezone.get_current_timezone()
        month_start_dt = timezone.make_aware(datetime.combine(month_start, time.min), tz)
        today_end_dt = timezone.make_aware(datetime.combine(today, time.max), tz)
        range_start_dt = timezone.make_aware(datetime.combine(range_start, time.min), tz)

        marcaciones_month_total = Marcacion.objects.filter(
            fecha_hora__gte=month_start_dt,
            fecha_hora__lte=today_end_dt,
        ).count()

        dispositivos_activos = Dispositivo.objects.filter(activo=True).count()

        attended_map = {
            item["day"]: item["count"]
            for item in Marcacion.objects.filter(
                fecha_hora__gte=range_start_dt,
                fecha_hora__lte=today_end_dt,
            )
            .annotate(day=TruncDate("fecha_hora"))
            .values("day")
            .annotate(count=Count("personal", distinct=True))
        }

        covered_by_day = defaultdict(set)
        justificados = Justificacion.objects.filter(
            estado=Justificacion.Estado.AUTORIZADO,
            fecha_inicio__lte=today,
            fecha_fin__gte=range_start,
        ).values("personal_id", "fecha_inicio", "fecha_fin")
        descansos = DescansoMedico.objects.filter(
            fecha_inicio__lte=today,
            fecha_fin__gte=range_start,
        ).values("personal_id", "fecha_inicio", "fecha_fin")

        for item in list(justificados) + list(descansos):
            start = max(item["fecha_inicio"], range_start)
            end = min(item["fecha_fin"], today)
            current = start
            while current <= end:
                covered_by_day[current].add(item["personal_id"])
                current += timedelta(days=1)

        asistencia_diaria = []
        current = range_start
        while current <= today:
            attended = int(attended_map.get(current, 0))
            covered = len(covered_by_day.get(current, set()))
            faltas = max(active_personal - attended - covered, 0)
            asistencia_diaria.append(
                {
                    "fecha": current.isoformat(),
                    "attended": attended,
                    "covered": covered,
                    "faltas": faltas,
                }
            )
            current += timedelta(days=1)

        recent_marcaciones = [
            {
                "id": item.id,
                "personal": item.personal_id,
                "personal_nombre": item.personal.nombres_completos if item.personal_id else "",
                "fecha_hora": item.fecha_hora,
                "tipo_evento": item.tipo_evento,
            }
            for item in Marcacion.objects.select_related("personal")
            .only("id", "personal_id", "personal__nombres_completos", "fecha_hora", "tipo_evento")
            .order_by("-fecha_hora")[:6]
        ]

        recent_justificaciones = [
            {
                "id": item.id,
                "personal": item.personal_id,
                "personal_nombre": item.personal.nombres_completos if item.personal_id else "",
                "motivo": item.motivo,
                "estado": item.estado,
                "fecha_inicio": item.fecha_inicio,
                "fecha_fin": item.fecha_fin,
            }
            for item in Justificacion.objects.select_related("personal")
            .only(
                "id",
                "personal_id",
                "personal__nombres_completos",
                "motivo",
                "estado",
                "fecha_inicio",
                "fecha_fin",
            )
            .order_by("-created_at")[:6]
        ]

        payload = {
            "summary": {
                "personal_total": personal_total,
                "personal_activo": active_personal,
                "marcaciones_mes": marcaciones_month_total,
                "justificaciones_total": justificaciones_total,
                "justificaciones_pendientes": pending_justificaciones,
                "boletas_mes_total": boletas_month_total,
                "boletas_mes_neto": boletas_month_neto,
                "dispositivos_activos": dispositivos_activos,
            },
            "asistencia_diaria": asistencia_diaria,
            "recent_marcaciones": recent_marcaciones,
            "recent_justificaciones": recent_justificaciones,
            "generated_at": timezone.now().isoformat(),
        }
        cache.set(cache_key, payload, timeout=300)
        return Response(payload)

    @staticmethod
    def _parse_days(raw_value):
        try:
            parsed = int(raw_value or 30)
        except (TypeError, ValueError):
            return 30
        return min(max(parsed, 7), 60)

__all__ = [
    "ReporteAsistenciaDiariaViewSet",
    "ReporteConceptoPersonalViewSet",
    "ReporteIncidenciaPersonalViewSet",
    "ReportePersonalMensualViewSet",
    "build_boleta_detalle",
    "build_reporte_general_payload",
    "ApiRootView",
    "DashboardResumenView",
    "HealthCheckView",
    "sync_reporte_general",
]
