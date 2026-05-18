import calendar
from datetime import date

from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.boleta_mensual.models import BoletaMensual
from apps.core.api import BaseModelViewSet
from apps.descanso_medico.models import DescansoMedico
from apps.justificacion.models import Justificacion
from apps.marcacion.models import Marcacion
from apps.personal.models.personal import Personal
from apps.personal.models.ubicacion_geografica import UbicacionGeografica
from apps.personal.selectors import filter_personal_queryset, get_personal_queryset
from apps.personal.serializers import (
    PersonalProcesarAsistenciaSerializer,
    PersonalSerializer,
    UbicacionGeograficaSerializer,
)
from apps.core.utils import date_range, get_boleta_conceptos, MONTH_LABELS
from apps.reportes.services import build_boleta_detalle, sync_reporte_general



def _build_dias_sets(justificaciones, descansos, fecha_inicio, fecha_fin):
    dias_justificados = {
        d
        for item in justificaciones
        if item.estado == Justificacion.Estado.AUTORIZADO
        for d in date_range(max(item.fecha_inicio, fecha_inicio), min(item.fecha_fin, fecha_fin))
    }
    dias_descanso = {
        d
        for item in descansos
        for d in date_range(max(item.fecha_inicio, fecha_inicio), min(item.fecha_fin, fecha_fin))
    }
    return dias_justificados, dias_descanso


def _build_personal_payload(personal):
    return {
        "id": personal.id,
        "codigo_empleado": personal.codigo_empleado,
        "numero_documento": personal.numero_documento,
        "nombres_completos": personal.nombres_completos,
        "empresa": {
            "id": personal.empresa_id,
            "razon_social": personal.empresa.razon_social if personal.empresa_id else "",
            "ruc": personal.empresa.ruc if personal.empresa_id else "",
        },
        "sucursal": personal.sucursal_id,
        "sucursal_nombre": personal.sucursal.nombre if personal.sucursal_id else "",
        "area": personal.area_id,
        "area_nombre": personal.area.nombre if personal.area_id else "",
        "tipo_documento": personal.tipo_documento or "",
        "tipo_trabajador_codigo": personal.tipo_trabajador.codigo if personal.tipo_trabajador_id else "",
        "tipo_trabajador": personal.tipo_trabajador.descripcion if personal.tipo_trabajador_id else "",
        "categoria_codigo": personal.categoria.codigo if personal.categoria_id else "",
        "categoria": personal.categoria.descripcion if personal.categoria_id else "",
        "cargo": personal.cargo.descripcion if personal.cargo_id else "",
        "fecha_ingreso": personal.fecha_ingreso.isoformat() if personal.fecha_ingreso else "",
    }


class PersonalPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class UbicacionGeograficaViewSet(BaseModelViewSet):
    queryset = UbicacionGeografica.objects.all()
    serializer_class = UbicacionGeograficaSerializer


class PersonalViewSet(BaseModelViewSet):
    queryset = get_personal_queryset()
    serializer_class = PersonalSerializer
    pagination_class = PersonalPagination

    def get_queryset(self):
        queryset = get_personal_queryset()
        search_term = (self.request.query_params.get("q") or self.request.query_params.get("search") or "").strip()
        return filter_personal_queryset(
            queryset,
            empresa=self.request.query_params.get("empresa"),
            sucursal=self.request.query_params.get("sucursal"),
            area=self.request.query_params.get("area"),
            estado=self.request.query_params.get("estado"),
            q=search_term,
        ).order_by("nombres_completos")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        use_lite = str(request.query_params.get("lite", "")).strip().lower() in {"1", "true", "yes"}
        paginated_param = str(request.query_params.get("paginated", "")).strip().lower()
        pagination_disabled = paginated_param in {"0", "false", "no"}
        use_pagination = (use_lite or paginated_param in {"1", "true", "yes"}) and not pagination_disabled
        serializer_class = PersonalProcesarAsistenciaSerializer if use_lite else self.get_serializer_class()
        if use_pagination:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = serializer_class(page, many=True, context=self.get_serializer_context())
                return self.get_paginated_response(serializer.data)
        serializer = serializer_class(queryset, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="resumen-planilla")
    def resumen_planilla(self, request, pk=None):
        personal = (
            Personal.objects
            .select_related("empresa", "sucursal", "area", "tipo_trabajador", "categoria", "cargo")
            .filter(pk=pk)
            .first()
        )
        if personal is None:
            return Response({"detail": "Personal no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            anio = int(request.query_params.get("anio") or now().year)
            mes = int(request.query_params.get("mes") or now().month)
        except (TypeError, ValueError):
            return Response({"detail": "anio y mes deben ser numericos."}, status=status.HTTP_400_BAD_REQUEST)
        if mes < 1 or mes > 12:
            return Response({"detail": "mes debe estar entre 1 y 12."}, status=status.HTTP_400_BAD_REQUEST)

        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fecha_inicio = date(anio, mes, 1)
        fecha_fin = date(anio, mes, ultimo_dia)

        boleta = (
            BoletaMensual.objects
            .filter(personal=personal, anio=anio, mes=mes)
            .prefetch_related("conceptos")
            .order_by("-created_at")
            .first()
        )
        conceptos = get_boleta_conceptos(boleta)

        justificaciones = list(
            Justificacion.objects
            .filter(personal=personal, fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_inicio)
            .order_by("fecha_inicio", "id")
        )
        descansos = list(
            DescansoMedico.objects
            .filter(personal=personal, fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_inicio)
            .order_by("fecha_inicio", "id")
        )
        marcaciones = list(
            Marcacion.objects
            .filter(personal=personal, fecha_hora__date__gte=fecha_inicio, fecha_hora__date__lte=fecha_fin)
            .order_by("fecha_hora", "id")
        )

        dias_con_marcacion = {item.fecha_hora.date() for item in marcaciones}
        dias_justificados, dias_descanso = _build_dias_sets(justificaciones, descansos, fecha_inicio, fecha_fin)

        cubiertos = dias_con_marcacion | dias_justificados | dias_descanso
        faltas = [
            d.isoformat()
            for d in date_range(fecha_inicio, fecha_fin)
            if d not in cubiertos
        ]

        return Response(
            {
                "personal": _build_personal_payload(personal),
                "periodo": {
                    "anio": anio,
                    "mes": mes,
                    "fecha_inicio": fecha_inicio.isoformat(),
                    "fecha_fin": fecha_fin.isoformat(),
                    "etiqueta": f"{MONTH_LABELS[mes]} {anio}",
                    "etiqueta_corta": f"{mes:02d}/{anio}",
                },
                "boleta": {
                    "id": boleta.id if boleta else None,
                    "sueldo_base": str(boleta.sueldo_base) if boleta else "0.00",
                    "total_ingresos": str(boleta.total_ingresos) if boleta else "0.00",
                    "total_descuentos": str(boleta.total_descuentos) if boleta else "0.00",
                    "neto_pagar": str(boleta.neto_pagar) if boleta else "0.00",
                    "estado": boleta.estado if boleta else "NO_GENERADA",
                    "conceptos": [
                        {"id": c.id, "tipo": c.tipo, "concepto": c.concepto, "monto": str(c.monto)}
                        for c in conceptos
                    ],
                },
                "boleta_detalle": build_boleta_detalle(
                    personal=personal,
                    boleta=boleta,
                    anio=anio,
                    mes=mes,
                    dias_con_marcacion=dias_con_marcacion,
                    dias_justificados=dias_justificados,
                    dias_descanso=dias_descanso,
                    faltas=faltas,
                ),
                "resumen": {
                    "dias_periodo": ultimo_dia,
                    "dias_con_marcacion": len(dias_con_marcacion),
                    "dias_justificados": len(dias_justificados),
                    "dias_descanso_medico": len(dias_descanso),
                    "dias_falta": len(faltas),
                },
                "faltas": faltas,
                "justificaciones": [
                    {
                        "id": j.id,
                        "motivo": j.motivo,
                        "estado": j.estado,
                        "tipo": j.tipo,
                        "fecha_inicio": j.fecha_inicio.isoformat(),
                        "fecha_fin": j.fecha_fin.isoformat(),
                        "dias": j.dias,
                        "nombre_documento": j.nombre_documento,
                    }
                    for j in justificaciones
                ],
                "descansos_medicos": [
                    {
                        "id": d.id,
                        "motivo": d.motivo,
                        "fecha_inicio": d.fecha_inicio.isoformat(),
                        "fecha_fin": d.fecha_fin.isoformat(),
                        "dias": d.dias,
                        "citt": d.citt,
                        "diagnostico": d.diagnostico,
                    }
                    for d in descansos
                ],
                "marcaciones": [
                    {
                        "id": m.id,
                        "fecha_hora": m.fecha_hora.isoformat(),
                        "tipo_evento": m.tipo_evento,
                        "codigo_equipo": m.codigo_equipo,
                    }
                    for m in marcaciones
                ],
            }
        )

    @action(detail=True, methods=["get"], url_path="reporte-general")
    def reporte_general(self, request, pk=None):
        personal = (
            Personal.objects
            .select_related("empresa", "sucursal", "area", "tipo_trabajador", "categoria", "cargo")
            .filter(pk=pk)
            .first()
        )
        if personal is None:
            return Response({"detail": "Personal no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        try:
            anio = int(request.query_params.get("anio") or now().year)
            mes = int(request.query_params.get("mes") or now().month)
        except (TypeError, ValueError):
            return Response({"detail": "anio y mes deben ser numericos."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = sync_reporte_general(personal, anio, mes)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(payload)
