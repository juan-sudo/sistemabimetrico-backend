from rest_framework import serializers

from apps.descarga_marcacion.models import DescargaMarcacion


class DescargaMarcacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescargaMarcacion
        fields = "__all__"
