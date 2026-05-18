from apps.core.api import BaseModelViewSet
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.conexion_equipo_biometrico.services import BiometricConnectionError, probe_device_connection
from apps.dispositivo.models import Dispositivo
from apps.dispositivo.serializers import DispositivoSerializer


class DispositivoPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class DispositivoAsistenciaMixin:
    @action(detail=False, methods=["post"], url_path="probar-conexion")
    def probar_conexion(self, request):
        try:
            password = int(request.data.get("clave_comunicacion") or 0)
        except (TypeError, ValueError):
            return Response(
                {"detail": "La clave de comunicacion debe ser numerica."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dispositivo_id = request.data.get("dispositivo_id")
        host = ""
        port = 4370
        nombre = ""

        if dispositivo_id:
            try:
                dispositivo = Dispositivo.objects.get(pk=int(dispositivo_id))
            except (TypeError, ValueError, Dispositivo.DoesNotExist):
                return Response(
                    {"detail": "Dispositivo no encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            host = dispositivo.direccion
            port = dispositivo.puerto
            nombre = dispositivo.nombre
        else:
            host = (request.data.get("direccion") or "").strip()
            nombre = (request.data.get("nombre") or "").strip()
            try:
                port = int(request.data.get("puerto") or 4370)
            except (TypeError, ValueError):
                return Response(
                    {"detail": "El puerto debe ser numerico."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not host:
            return Response(
                {"detail": "La direccion IP o dominio es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = probe_device_connection(host=host, port=port, password=password)
        except BiometricConnectionError as exc:
            return Response(
                {
                    "ok": False,
                    "estado": "error",
                    "nombre": nombre or host,
                    "host": host,
                    "port": port,
                    "detalle": str(exc),
                },
                status=status.HTTP_200_OK,
            )

        return Response({"ok": True, "nombre": nombre or host, **result})


class DispositivoViewSet(BaseModelViewSet, DispositivoAsistenciaMixin):
    queryset = Dispositivo.objects.only(
        "id",
        "nombre",
        "direccion_tipo",
        "direccion",
        "comunicacion",
        "puerto",
        "uso",
        "activo",
    ).order_by("nombre")
    serializer_class = DispositivoSerializer
    pagination_class = DispositivoPagination

    def list(self, request, *args, **kwargs):
        paginated_param = str(request.query_params.get("paginated", "")).strip().lower()
        use_pagination = paginated_param not in {"0", "false", "no"}

        queryset = self.filter_queryset(self.get_queryset())

        if use_pagination:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        q = (self.request.query_params.get("q") or self.request.query_params.get("search") or "").strip()
        uso = (self.request.query_params.get("uso") or "").strip()
        activo = (self.request.query_params.get("activo") or "").strip().lower()

        if uso:
            queryset = queryset.filter(uso=uso)

        if activo in {"1", "true", "si", "sí", "activo"}:
            queryset = queryset.filter(activo=True)
        elif activo in {"0", "false", "no", "inactivo"}:
            queryset = queryset.filter(activo=False)

        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(comunicacion__icontains=q)
                | Q(direccion__icontains=q)
                | Q(uso__icontains=q)
            )
        return queryset
