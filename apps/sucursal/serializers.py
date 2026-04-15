from rest_framework import serializers

from apps.sucursal.models import Sucursal
from apps.sucursal.services import build_sucursal_label


class SucursalSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.razon_social", read_only=True)
    empresa_codigo = serializers.CharField(source="empresa.codigo", read_only=True)
    descripcion = serializers.SerializerMethodField()

    def get_descripcion(self, obj):
        return build_sucursal_label(obj)

    class Meta:
        model = Sucursal
        fields = "__all__"
