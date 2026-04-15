from rest_framework import serializers

from apps.marcacion.models import Marcacion


class MarcacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marcacion
        fields = "__all__"
