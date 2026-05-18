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
    tipo_documento_nombre = serializers.SerializerMethodField()
    tipo_trabajador_nombre = serializers.CharField(source="tipo_trabajador.descripcion", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.descripcion", read_only=True)
    tipo_sindicato_nombre = serializers.CharField(source="tipo_sindicato.descripcion", read_only=True)
    cargo_nombre = serializers.CharField(source="cargo.descripcion", read_only=True)
    direccion_nombre = serializers.SerializerMethodField()

    def get_tipo_documento_nombre(self, obj):
        return (obj.tipo_documento or "").strip() or None

    def get_direccion_nombre(self, obj):
        return (obj.direccion or "").strip() or None

    class Meta:
        model = Personal
        fields = "__all__"


class PersonalProcesarAsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personal
        fields = (
            "id",
            "empresa",
            "sucursal",
            "area",
            "numero_documento",
            "codigo_empleado",
            "nombres_completos",
        )


class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = "__all__"


__all__ = [
    "DispositivoSerializer",
    "PersonalProcesarAsistenciaSerializer",
    "PersonalSerializer",
    "UbicacionGeograficaSerializer",
]
