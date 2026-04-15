from rest_framework import serializers

from apps.boleta_concepto.models import BoletaConcepto


class BoletaConceptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoletaConcepto
        fields = "__all__"


__all__ = ["BoletaConceptoSerializer"]
