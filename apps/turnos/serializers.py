from rest_framework import serializers

from apps.turnos.models.personal_turno import PersonalTurno
from apps.turnos.models.turno import Turno
from apps.turnos.models.turno_bloque_horario import TurnoBloqueHorario
from apps.turnos.services import build_turno_label, format_turno_horario


class TurnoSerializer(serializers.ModelSerializer):
    horario = serializers.SerializerMethodField()
    descripcion_larga = serializers.SerializerMethodField()
    bloques_detalle = serializers.SerializerMethodField()

    def to_representation(self, instance):
        # Compute bloques once per object; reused by all SerializerMethodFields below.
        self._bloques = list(instance.bloques.all())
        return super().to_representation(instance)

    def get_horario(self, obj):
        return format_turno_horario(self._bloques)

    def get_descripcion_larga(self, obj):
        return build_turno_label(obj)

    def get_bloques_detalle(self, obj):
        return [
            {
                "id": item.id,
                "turno": item.turno_id,
                "orden": item.orden,
                "hora_entrada": item.hora_entrada.isoformat(),
                "hora_salida": item.hora_salida.isoformat(),
            }
            for item in self._bloques
        ]

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
    horario = serializers.SerializerMethodField()
    hora_entrada = serializers.SerializerMethodField()
    hora_salida = serializers.SerializerMethodField()

    def to_representation(self, instance):
        # Sort once per object; reused by horario, hora_entrada and hora_salida.
        self._bloques = sorted(list(instance.turno.bloques.all()), key=lambda b: b.orden)
        return super().to_representation(instance)

    def get_horario(self, obj):
        if not self._bloques:
            return "-"
        return " / ".join(
            f"{b.hora_entrada.strftime('%H:%M')}-{b.hora_salida.strftime('%H:%M')}"
            for b in self._bloques
        )

    def get_hora_entrada(self, obj):
        if not self._bloques:
            return "-"
        return " / ".join(b.hora_entrada.strftime("%H:%M") for b in self._bloques)

    def get_hora_salida(self, obj):
        if not self._bloques:
            return "-"
        return " / ".join(b.hora_salida.strftime("%H:%M") for b in self._bloques)

    class Meta:
        model = PersonalTurno
        fields = "__all__"


__all__ = [
    "PersonalTurnoSerializer",
    "TurnoBloqueHorarioSerializer",
    "TurnoSerializer",
]
