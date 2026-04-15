from django.db import models
from django.utils.timezone import now
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api import BaseModelViewSet
from apps.justificacion.models import Justificacion
from apps.justificacion.serializers import JustificacionSerializer


class JustificacionViewSet(BaseModelViewSet):
    queryset = Justificacion.objects.select_related(
        "personal",
        "sucursal",
        "area",
        "gestionado_por",
    ).all()
    serializer_class = JustificacionSerializer
    pagination_class = None

    class Pagination(PageNumberPagination):
        page_size = 50
        page_size_query_param = "page_size"
        max_page_size = 200

    def get_queryset(self):
        queryset = super().get_queryset()
        sucursal = self.request.query_params.get("sucursal")
        area = self.request.query_params.get("area")
        motivo = self.request.query_params.get("motivo")
        fecha = self.request.query_params.get("fecha")
        mes = self.request.query_params.get("mes")
        anio = self.request.query_params.get("anio")
        estado = self.request.query_params.get("estado")
        q = self.request.query_params.get("q") or self.request.query_params.get("search")

        if sucursal:
            queryset = queryset.filter(sucursal_id=sucursal)
        if area:
            queryset = queryset.filter(area_id=area)
        if motivo:
            queryset = queryset.filter(motivo__icontains=motivo)
        if fecha:
            queryset = queryset.filter(fecha_inicio=fecha)
        if mes:
            queryset = queryset.filter(fecha_inicio__month=mes)
        if anio:
            queryset = queryset.filter(fecha_inicio__year=anio)
        if estado:
            queryset = queryset.filter(estado=estado)
        if q:
            queryset = queryset.filter(
                models.Q(personal__nombres_completos__icontains=q)
                | models.Q(personal__numero_documento__icontains=q)
                | models.Q(numero_documento__icontains=q)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        use_pagination = str(request.query_params.get("paginated", "")).strip().lower() in {"1", "true", "yes"}
        if use_pagination:
            paginator = self.Pagination()
            page = paginator.paginate_queryset(queryset, request, view=self)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="gestionar")
    def gestionar(self, request):
        ids = request.data.get("ids") or []
        accion = (request.data.get("accion") or "").upper()
        motivo = (request.data.get("motivo") or "").strip()

        if not isinstance(ids, list) or not ids:
            return Response({"detail": "Debe enviar ids como lista no vacia."}, status=status.HTTP_400_BAD_REQUEST)

        valid_ids = []
        for item in ids:
            try:
                valid_ids.append(int(item))
            except (TypeError, ValueError):
                continue

        if not valid_ids:
            return Response({"detail": "No se enviaron IDs validos."}, status=status.HTTP_400_BAD_REQUEST)

        if accion not in {"AUTORIZAR", "NO_AUTORIZAR"}:
            return Response(
                {"detail": "accion invalida. Use AUTORIZAR o NO_AUTORIZAR."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if accion == "NO_AUTORIZAR" and not motivo:
            return Response({"detail": "Debe enviar motivo para no autorizar."}, status=status.HTTP_400_BAD_REQUEST)

        estado_target = (
            Justificacion.Estado.AUTORIZADO if accion == "AUTORIZAR" else Justificacion.Estado.NO_AUTORIZADO
        )

        payload = {
            "estado": estado_target,
            "gestionado_por": request.user if request.user.is_authenticated else None,
            "fecha_gestion": now(),
        }

        if accion == "AUTORIZAR":
            payload["motivo_no_autorizacion"] = ""
        else:
            payload["motivo_no_autorizacion"] = motivo

        updated = Justificacion.objects.filter(id__in=valid_ids).update(**payload)
        return Response({"actualizados": updated, "estado": estado_target})
