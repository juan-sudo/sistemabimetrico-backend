from rest_framework import serializers

from apps.descanso_medico.models import DescansoMedico


class DescansoMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescansoMedico
        fields = "__all__"
