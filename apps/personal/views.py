import calendar
from datetime import date, timedelta

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
from apps.personal.serializers import PersonalSerializer, UbicacionGeograficaSerializer
from apps.reportes.services import build_boleta_detalle, sync_reporte_general

MONTH_LABELS = ("", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")


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
        use_pagination = str(request.query_params.get("paginated", "")).strip().lower() in {"1", "true", "yes"}
        if use_pagination:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="resumen-planilla")
    def resumen_planilla(self, request, pk=None):
        personal = Personal.objects.select_related("empresa", "sucursal", "area", "tipo_documento", "tipo_trabajador", "categoria", "cargo").filter(pk=pk).first()
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
        boleta = BoletaMensual.objects.filter(personal=personal, anio=anio, mes=mes).prefetch_related("conceptos").order_by("-created_at").first()
        conceptos = list(boleta.conceptos.all().order_by("tipo", "concepto", "id")) if boleta else []
        justificaciones = list(Justificacion.objects.filter(personal=personal, fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_inicio).order_by("fecha_inicio", "id"))
        descansos = list(DescansoMedico.objects.filter(personal=personal, fecha_inicio__lte=fecha_fin, fecha_fin__gte=fecha_inicio).order_by("fecha_inicio", "id"))
        marcaciones = list(Marcacion.objects.filter(personal=personal, fecha_hora__date__gte=fecha_inicio, fecha_hora__date__lte=fecha_fin).order_by("fecha_hora", "id"))

        dias_con_marcacion = {item.fecha_hora.date() for item in marcaciones}
        dias_justificados, dias_descanso = set(), set()
        for item in justificaciones:
            current = max(item.fecha_inicio, fecha_inicio)
            end = min(item.fecha_fin, fecha_fin)
            while current <= end:
                if item.estado == Justificacion.Estado.AUTORIZADO:
                    dias_justificados.add(current)
                current += timedelta(days=1)
        for item in descansos:
            current = max(item.fecha_inicio, fecha_inicio)
            end = min(item.fecha_fin, fecha_fin)
            while current <= end:
                dias_descanso.add(current)
                current += timedelta(days=1)

        faltas = []
        for offset in range(ultimo_dia):
            current = fecha_inicio + timedelta(days=offset)
            if current in dias_con_marcacion or current in dias_justificados or current in dias_descanso:
                continue
            faltas.append(current.isoformat())

        return Response(
            {
                "personal": {
                    "id": personal.id,
                    "codigo_empleado": personal.codigo_empleado,
                    "numero_documento": personal.numero_documento,
                    "nombres_completos": personal.nombres_completos,
                    "empresa": {"id": personal.empresa_id, "razon_social": personal.empresa.razon_social if personal.empresa_id else "", "ruc": personal.empresa.ruc if personal.empresa_id else ""},
                    "sucursal": personal.sucursal_id,
                    "sucursal_nombre": personal.sucursal.nombre if personal.sucursal_id else "",
                    "area": personal.area_id,
                    "area_nombre": personal.area.nombre if personal.area_id else "",
                    "tipo_documento": personal.tipo_documento.descripcion if personal.tipo_documento_id else "",
                    "tipo_trabajador_codigo": personal.tipo_trabajador.codigo if personal.tipo_trabajador_id else "",
                    "tipo_trabajador": personal.tipo_trabajador.descripcion if personal.tipo_trabajador_id else "",
                    "categoria_codigo": personal.categoria.codigo if personal.categoria_id else "",
                    "categoria": personal.categoria.descripcion if personal.categoria_id else "",
                    "cargo": personal.cargo.descripcion if personal.cargo_id else "",
                    "fecha_ingreso": personal.fecha_ingreso.isoformat() if personal.fecha_ingreso else "",
                },
                "periodo": {"anio": anio, "mes": mes, "fecha_inicio": fecha_inicio.isoformat(), "fecha_fin": fecha_fin.isoformat(), "etiqueta": f"{MONTH_LABELS[mes]} {anio}", "etiqueta_corta": f"{mes:02d}/{anio}"},
                "boleta": {
                    "id": boleta.id if boleta else None,
                    "sueldo_base": str(boleta.sueldo_base) if boleta else "0.00",
                    "total_ingresos": str(boleta.total_ingresos) if boleta else "0.00",
                    "total_descuentos": str(boleta.total_descuentos) if boleta else "0.00",
                    "neto_pagar": str(boleta.neto_pagar) if boleta else "0.00",
                    "estado": boleta.estado if boleta else "NO_GENERADA",
                    "conceptos": [{"id": item.id, "tipo": item.tipo, "concepto": item.concepto, "monto": str(item.monto)} for item in conceptos],
                },
                "boleta_detalle": build_boleta_detalle(personal=personal, boleta=boleta, anio=anio, mes=mes, dias_con_marcacion=dias_con_marcacion, dias_justificados=dias_justificados, dias_descanso=dias_descanso, faltas=faltas),
                "resumen": {"dias_periodo": ultimo_dia, "dias_con_marcacion": len(dias_con_marcacion), "dias_justificados": len(dias_justificados), "dias_descanso_medico": len(dias_descanso), "dias_falta": len(faltas)},
                "faltas": faltas,
                "justificaciones": [{"id": item.id, "motivo": item.motivo, "estado": item.estado, "tipo": item.tipo, "fecha_inicio": item.fecha_inicio.isoformat(), "fecha_fin": item.fecha_fin.isoformat(), "dias": item.dias, "nombre_documento": item.nombre_documento} for item in justificaciones],
                "descansos_medicos": [{"id": item.id, "motivo": item.motivo, "fecha_inicio": item.fecha_inicio.isoformat(), "fecha_fin": item.fecha_fin.isoformat(), "dias": item.dias, "citt": item.citt, "diagnostico": item.diagnostico} for item in descansos],
                "marcaciones": [{"id": item.id, "fecha_hora": item.fecha_hora.isoformat(), "tipo_evento": item.tipo_evento, "codigo_equipo": item.codigo_equipo} for item in marcaciones],
            }
        )

    @action(detail=True, methods=["get"], url_path="reporte-general")
    def reporte_general(self, request, pk=None):
        personal = Personal.objects.select_related("empresa", "sucursal", "area", "tipo_documento", "tipo_trabajador", "categoria", "cargo").filter(pk=pk).first()
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
