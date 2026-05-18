from rest_framework import serializers

from apps.justificacion.models import Justificacion


class JustificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Justificacion
        fields = "__all__"


class JustificacionLiteSerializer(serializers.ModelSerializer):
    personal_nombres_completos = serializers.CharField(source="personal.nombres_completos", read_only=True)
    personal_numero_documento = serializers.CharField(source="personal.numero_documento", read_only=True)
    sucursal_nombre = serializers.CharField(source="sucursal.nombre", read_only=True)
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)

    class Meta:
        model = Justificacion
        fields = (
            "id",
            "personal",
            "sucursal",
            "area",
            "motivo",
            "tipo",
            "rango",
            "fecha_inicio",
            "fecha_fin",
            "dias",
            "descripcion",
            "tiene_adjunto",
            "numero_documento",
            "nombre_documento",
            "estado",
            "motivo_no_autorizacion",
            "personal_nombres_completos",
            "personal_numero_documento",
            "sucursal_nombre",
            "area_nombre",
        )
