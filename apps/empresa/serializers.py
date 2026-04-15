from rest_framework import serializers

from apps.empresa.models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = "__all__"


class EmpresaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ("id", "codigo", "razon_social", "ruc", "correo", "logo", "activo")
