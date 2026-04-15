from rest_framework import serializers

from apps.boleta_mensual.models import BoletaMensual


class BoletaMensualSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoletaMensual
        fields = "__all__"
