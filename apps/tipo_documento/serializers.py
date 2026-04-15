from rest_framework import serializers

from apps.tipo_documento.models import TipoDocumento
from apps.tipo_documento.services import build_tipo_documento_label


class TipoDocumentoSerializer(serializers.ModelSerializer):
    descripcion_larga = serializers.SerializerMethodField()

    def get_descripcion_larga(self, obj):
        return build_tipo_documento_label(obj)

    class Meta:
        model = TipoDocumento
        fields = "__all__"
