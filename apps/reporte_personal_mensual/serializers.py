from rest_framework import serializers

from apps.reporte_personal_mensual.models import ReportePersonalMensual
from apps.reporte_personal_mensual.services import build_periodo_label, build_resumen_label


class ReportePersonalMensualSerializer(serializers.ModelSerializer):
    personal_codigo_empleado = serializers.CharField(source="personal.codigo_empleado", read_only=True)
    personal_numero_documento = serializers.CharField(source="personal.numero_documento", read_only=True)
    personal_nombres_completos = serializers.CharField(source="personal.nombres_completos", read_only=True)
    empresa_nombre = serializers.CharField(source="personal.empresa.razon_social", read_only=True)
    sucursal_nombre = serializers.CharField(source="personal.sucursal.nombre", read_only=True)
    area_nombre = serializers.CharField(source="personal.area.nombre", read_only=True)
    tipo_documento_nombre = serializers.CharField(source="personal.tipo_documento.descripcion", read_only=True)
    tipo_trabajador_nombre = serializers.CharField(source="personal.tipo_trabajador.descripcion", read_only=True)
    categoria_nombre = serializers.CharField(source="personal.categoria.descripcion", read_only=True)
    cargo_nombre = serializers.CharField(source="personal.cargo.descripcion", read_only=True)
    periodo = serializers.SerializerMethodField()
    resumen = serializers.SerializerMethodField()

    def get_periodo(self, obj):
        return build_periodo_label(obj.anio, obj.mes)

    def get_resumen(self, obj):
        return build_resumen_label(obj)

    class Meta:
        model = ReportePersonalMensual
        fields = "__all__"


__all__ = ["ReportePersonalMensualSerializer"]
