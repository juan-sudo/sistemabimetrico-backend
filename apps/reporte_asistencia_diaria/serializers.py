from rest_framework import serializers

from apps.reporte_asistencia_diaria.models import ReporteAsistenciaDiaria
from apps.reporte_asistencia_diaria.services import build_periodo_label, format_time_value


class ReporteAsistenciaDiariaSerializer(serializers.ModelSerializer):
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
    hora_entrada_programada_texto = serializers.SerializerMethodField()
    hora_salida_programada_texto = serializers.SerializerMethodField()
    hora_entrada_real_texto = serializers.SerializerMethodField()
    hora_salida_real_texto = serializers.SerializerMethodField()

    def get_reporte_periodo(self, obj):
        return build_periodo_label(obj.reporte.anio, obj.reporte.mes)

    def get_hora_entrada_programada_texto(self, obj):
        return format_time_value(obj.hora_entrada_programada)

    def get_hora_salida_programada_texto(self, obj):
        return format_time_value(obj.hora_salida_programada)

    def get_hora_entrada_real_texto(self, obj):
        return format_time_value(obj.hora_entrada_real)

    def get_hora_salida_real_texto(self, obj):
        return format_time_value(obj.hora_salida_real)

    class Meta:
        model = ReporteAsistenciaDiaria
        fields = "__all__"


__all__ = ["ReporteAsistenciaDiariaSerializer"]
