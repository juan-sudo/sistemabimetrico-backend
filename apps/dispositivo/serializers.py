from rest_framework import serializers

from apps.dispositivo.models import Dispositivo


class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = "__all__"


__all__ = ["DispositivoSerializer"]
