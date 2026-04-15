from rest_framework import serializers

from apps.reporte_concepto_personal.models import ReporteConceptoPersonal
from apps.reporte_concepto_personal.services import build_periodo_label


class ReporteConceptoPersonalSerializer(serializers.ModelSerializer):
    personal_id = serializers.IntegerField(source="reporte.personal_id", read_only=True)
    personal_codigo_empleado = serializers.CharField(source="reporte.personal.codigo_empleado", read_only=True)
    personal_numero_documento = serializers.CharField(source="reporte.personal.numero_documento", read_only=True)
    personal_nombres_completos = serializers.CharField(source="reporte.personal.nombres_completos", read_only=True)
    empresa_nombre = serializers.CharField(source="reporte.personal.empresa.razon_social", read_only=True)
    sucursal_nombre = serializers.CharField(source="reporte.personal.sucursal.nombre", read_only=True)
    area_nombre = serializers.CharField(source="reporte.personal.area.nombre", read_only=True)
    reporte_anio = serializers.IntegerField(source="reporte.anio", read_only=True)
    reporte_mes = serializers.IntegerField(source="reporte.mes", read_only=True)
    reporte_periodo = serializers.SerializerMethodField()

    def get_reporte_periodo(self, obj):
        return build_periodo_label(obj.reporte.anio, obj.reporte.mes)

    class Meta:
        model = ReporteConceptoPersonal
        fields = "__all__"


__all__ = ["ReporteConceptoPersonalSerializer"]
