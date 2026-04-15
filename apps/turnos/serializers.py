from rest_framework import serializers

from apps.turnos.models.personal_turno import PersonalTurno
from apps.turnos.models.turno import Turno
from apps.turnos.models.turno_bloque_horario import TurnoBloqueHorario
from apps.turnos.services import build_turno_label, format_turno_horario


class TurnoSerializer(serializers.ModelSerializer):
    horario = serializers.SerializerMethodField()
    descripcion_larga = serializers.SerializerMethodField()

    def get_horario(self, obj):
        return format_turno_horario(obj.bloques.all())

    def get_descripcion_larga(self, obj):
        return build_turno_label(obj)

    class Meta:
        model = Turno
        fields = "__all__"


class TurnoBloqueHorarioSerializer(serializers.ModelSerializer):
    turno_codigo = serializers.CharField(source="turno.codigo", read_only=True)
    turno_nombre = serializers.CharField(source="turno.nombre", read_only=True)

    class Meta:
        model = TurnoBloqueHorario
        fields = "__all__"


class PersonalTurnoSerializer(serializers.ModelSerializer):
    personal_nombre = serializers.CharField(source="personal.nombres_completos", read_only=True)
    personal_documento = serializers.CharField(source="personal.numero_documento", read_only=True)
    sucursal_nombre = serializers.CharField(source="personal.sucursal.nombre", read_only=True)
    area_nombre = serializers.CharField(source="personal.area.nombre", read_only=True)
    turno_codigo = serializers.CharField(source="turno.codigo", read_only=True)
    turno_nombre = serializers.CharField(source="turno.nombre", read_only=True)

    class Meta:
        model = PersonalTurno
        fields = "__all__"


__all__ = [
    "PersonalTurnoSerializer",
    "TurnoBloqueHorarioSerializer",
    "TurnoSerializer",
]
