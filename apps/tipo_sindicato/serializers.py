from rest_framework import serializers

from apps.tipo_sindicato.models import TipoSindicato
from apps.tipo_sindicato.services import build_tipo_sindicato_label


class TipoSindicatoSerializer(serializers.ModelSerializer):
    descripcion_larga = serializers.SerializerMethodField()

    def get_descripcion_larga(self, obj):
        return build_tipo_sindicato_label(obj)

    class Meta:
        model = TipoSindicato
        fields = "__all__"
