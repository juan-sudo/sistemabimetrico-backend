from rest_framework import serializers

from apps.area.models import Area


class AreaSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        tipo = attrs.get("tipo", getattr(self.instance, "tipo", None))
        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        sucursal = attrs.get("sucursal", getattr(self.instance, "sucursal", None))

        if parent and sucursal and parent.sucursal_id != sucursal.id:
            raise serializers.ValidationError({"parent": "El area padre debe pertenecer a la misma sucursal."})

        if tipo in {"GERENCIA", "OFICINA"}:
            if parent is not None:
                raise serializers.ValidationError({"parent": "Gerencia y Oficina no deben tener area padre."})
        elif tipo == "SUBGERENCIA":
            if parent is None:
                raise serializers.ValidationError({"parent": "La Subgerencia debe depender de una Gerencia."})
            if parent.tipo != "GERENCIA":
                raise serializers.ValidationError({"parent": "La Subgerencia solo puede depender de una Gerencia."})
        elif tipo == "UNIDAD":
            if parent is None:
                raise serializers.ValidationError({"parent": "La Unidad debe depender de una Subgerencia."})
            if parent.tipo != "SUBGERENCIA":
                raise serializers.ValidationError({"parent": "La Unidad solo puede depender de una Subgerencia."})

        return attrs

    class Meta:
        model = Area
        fields = "__all__"
