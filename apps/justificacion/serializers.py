from rest_framework import serializers

from apps.justificacion.models import Justificacion


class JustificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Justificacion
        fields = "__all__"
