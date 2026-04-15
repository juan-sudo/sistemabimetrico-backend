from rest_framework import serializers

from apps.tipo_trabajador.models import TipoTrabajador
from apps.tipo_trabajador.services import build_tipo_trabajador_label


class TipoTrabajadorSerializer(serializers.ModelSerializer):
    descripcion_larga = serializers.SerializerMethodField()

    def get_descripcion_larga(self, obj):
        return build_tipo_trabajador_label(obj)

    class Meta:
        model = TipoTrabajador
        fields = "__all__"
