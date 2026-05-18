from rest_framework import serializers

from apps.marcacion.models import Marcacion


class MarcacionSerializer(serializers.ModelSerializer):
    personal_codigo_empleado = serializers.CharField(source="personal.codigo_empleado", read_only=True)
    personal_numero_documento = serializers.CharField(source="personal.numero_documento", read_only=True)
    personal_nombres_completos = serializers.CharField(source="personal.nombres_completos", read_only=True)
    personal_area = serializers.IntegerField(source="personal.area_id", read_only=True)

    class Meta:
        model = Marcacion
        fields = "__all__"


class MarcacionConsultarSerializer(serializers.ModelSerializer):
    personal_codigo_empleado = serializers.CharField(source="personal.codigo_empleado", read_only=True)
    personal_numero_documento = serializers.CharField(source="personal.numero_documento", read_only=True)
    personal_nombres_completos = serializers.CharField(source="personal.nombres_completos", read_only=True)
    personal_area = serializers.IntegerField(source="personal.area_id", read_only=True)

    class Meta:
        model = Marcacion
        fields = (
            "id",
            "personal",
            "dispositivo",
            "descarga",
            "fecha_hora",
            "codigo_equipo",
            "tipo_evento",
            "situacion",
            "personal_codigo_empleado",
            "personal_numero_documento",
            "personal_nombres_completos",
            "personal_area",
        )
