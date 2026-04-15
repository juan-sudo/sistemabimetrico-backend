from rest_framework import serializers

from apps.personal.models.dispositivo import Dispositivo
from apps.personal.models.personal import Personal
from apps.personal.models.ubicacion_geografica import UbicacionGeografica
from apps.personal.services import format_ubicacion_label


class UbicacionGeograficaSerializer(serializers.ModelSerializer):
    descripcion = serializers.SerializerMethodField()

    def get_descripcion(self, obj):
        return format_ubicacion_label(obj)

    class Meta:
        model = UbicacionGeografica
        fields = "__all__"


class PersonalSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.razon_social", read_only=True)
    sucursal_nombre = serializers.CharField(source="sucursal.nombre", read_only=True)
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)
    tipo_documento_nombre = serializers.CharField(source="tipo_documento.descripcion", read_only=True)
    tipo_trabajador_nombre = serializers.CharField(source="tipo_trabajador.descripcion", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.descripcion", read_only=True)
    tipo_sindicato_nombre = serializers.CharField(source="tipo_sindicato.descripcion", read_only=True)
    cargo_nombre = serializers.CharField(source="cargo.descripcion", read_only=True)
    ubicacion_nombre = serializers.SerializerMethodField()

    def get_ubicacion_nombre(self, obj):
        return format_ubicacion_label(obj.ubicacion)

    class Meta:
        model = Personal
        fields = "__all__"


class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = "__all__"


__all__ = [
    "DispositivoSerializer",
    "PersonalSerializer",
    "UbicacionGeograficaSerializer",
]
