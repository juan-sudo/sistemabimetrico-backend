from apps.core.api import BaseModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.conexion_equipo_biometrico.services import BiometricConnectionError, probe_device_connection
from apps.dispositivo.models import Dispositivo
from apps.dispositivo.serializers import DispositivoSerializer


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
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer
