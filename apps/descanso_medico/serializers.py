from rest_framework import serializers

from apps.descanso_medico.models import DescansoMedico


class DescansoMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescansoMedico
        fields = "__all__"


class DescansoMedicoLiteSerializer(serializers.ModelSerializer):
    personal_nombres_completos = serializers.CharField(source="personal.nombres_completos", read_only=True)
    personal_numero_documento = serializers.CharField(source="personal.numero_documento", read_only=True)
    personal_codigo_empleado = serializers.CharField(source="personal.codigo_empleado", read_only=True)
    personal_sucursal = serializers.IntegerField(source="personal.sucursal_id", read_only=True)
    personal_area = serializers.IntegerField(source="personal.area_id", read_only=True)
    personal_sucursal_nombre = serializers.CharField(source="personal.sucursal.nombre", read_only=True)
    personal_area_nombre = serializers.CharField(source="personal.area.nombre", read_only=True)

    class Meta:
        model = DescansoMedico
        fields = (
            "id",
            "personal",
            "motivo",
            "fecha_inicio",
            "fecha_fin",
            "dias",
            "citt",
            "diagnostico",
            "tiene_adjunto",
            "numero_documento",
            "personal_nombres_completos",
            "personal_numero_documento",
            "personal_codigo_empleado",
            "personal_sucursal",
            "personal_area",
            "personal_sucursal_nombre",
            "personal_area_nombre",
        )
