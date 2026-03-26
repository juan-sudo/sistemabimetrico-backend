from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Area,
    BoletaConcepto,
    BoletaMensual,
    Cargo,
    Categoria,
    DescansoMedico,
    DescargaMarcacion,
    Dispositivo,
    Empresa,
    Justificacion,
    LicenciaAgua,
    Marcacion,
    Personal,
    PersonalTurno,
    ReporteAsistenciaDiaria,
    ReporteConceptoPersonal,
    ReporteIncidenciaPersonal,
    ReportePersonalMensual,
    Sucursal,
    TipoDocumento,
    TipoSindicato,
    TipoTrabajador,
    Turno,
    TurnoBloqueHorario,
    UbicacionGeografica,
    UsuarioAgua,
    UsuarioModuloPermiso,
)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    module_permissions = serializers.SerializerMethodField(read_only=True)
    module_permissions_input = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    def get_module_permissions(self, obj):
        return [
            {
                "id": item.id,
                "modulo": item.modulo,
                "modulo_label": item.get_modulo_display(),
                "puede_ver": item.puede_ver,
                "puede_crear": item.puede_crear,
                "puede_editar": item.puede_editar,
                "puede_eliminar": item.puede_eliminar,
            }
            for item in obj.module_permissions.all().order_by("modulo")
        ]

    def _sync_module_permissions(self, user, raw_permissions):
        if raw_permissions is None:
            return
        user.module_permissions.all().delete()
        valid_modules = {choice[0] for choice in UsuarioModuloPermiso.Modulo.choices}
        rows = []
        for item in raw_permissions:
            modulo = str(item.get("modulo") or "").strip().upper()
            if modulo not in valid_modules:
                continue
            rows.append(
                UsuarioModuloPermiso(
                    user=user,
                    modulo=modulo,
                    puede_ver=bool(item.get("puede_ver", True)),
                    puede_crear=bool(item.get("puede_crear", False)),
                    puede_editar=bool(item.get("puede_editar", False)),
                    puede_eliminar=bool(item.get("puede_eliminar", False)),
                )
            )
        if rows:
            UsuarioModuloPermiso.objects.bulk_create(rows)

    def create(self, validated_data):
        password = validated_data.pop("password", "")
        raw_permissions = validated_data.pop("module_permissions_input", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        self._sync_module_permissions(user, raw_permissions)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        raw_permissions = validated_data.pop("module_permissions_input", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        self._sync_module_permissions(instance, raw_permissions)
        return instance

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "is_superuser",
            "password",
            "module_permissions",
            "module_permissions_input",
        )


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = "__all__"


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = "__all__"


class AreaSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        tipo = attrs.get("tipo", getattr(self.instance, "tipo", None))
        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        sucursal = attrs.get("sucursal", getattr(self.instance, "sucursal", None))

        if parent and sucursal and parent.sucursal_id != sucursal.id:
            raise serializers.ValidationError({"parent": "El area padre debe pertenecer a la misma sucursal."})

        if tipo in {"GERENCIA", "OFICINA"}:
            if parent is not None:
                raise serializers.ValidationError(
                    {"parent": "Gerencia y Oficina no deben tener area padre."}
                )
        elif tipo == "SUBGERENCIA":
            if parent is None:
                raise serializers.ValidationError(
                    {"parent": "La Subgerencia debe depender de una Gerencia."}
                )
            if parent.tipo != "GERENCIA":
                raise serializers.ValidationError(
                    {"parent": "La Subgerencia solo puede depender de una Gerencia."}
                )
        elif tipo == "UNIDAD":
            if parent is None:
                raise serializers.ValidationError(
                    {"parent": "La Unidad debe depender de una Subgerencia."}
                )
            if parent.tipo != "SUBGERENCIA":
                raise serializers.ValidationError(
                    {"parent": "La Unidad solo puede depender de una Subgerencia."}
                )

        return attrs

    class Meta:
        model = Area
        fields = "__all__"


class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = "__all__"


class TipoTrabajadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTrabajador
        fields = "__all__"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = "__all__"


class TipoSindicatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoSindicato
        fields = "__all__"


class UbicacionGeograficaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UbicacionGeografica
        fields = "__all__"


class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personal
        fields = "__all__"


class TurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = "__all__"


class TurnoBloqueHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurnoBloqueHorario
        fields = "__all__"


class PersonalTurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalTurno
        fields = "__all__"


class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = "__all__"


class DescargaMarcacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescargaMarcacion
        fields = "__all__"


class MarcacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marcacion
        fields = "__all__"


class JustificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Justificacion
        fields = "__all__"


class DescansoMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescansoMedico
        fields = "__all__"


class BoletaMensualSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoletaMensual
        fields = "__all__"


class BoletaConceptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoletaConcepto
        fields = "__all__"


class ReportePersonalMensualSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportePersonalMensual
        fields = "__all__"


class ReporteAsistenciaDiariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteAsistenciaDiaria
        fields = "__all__"


class ReporteConceptoPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteConceptoPersonal
        fields = "__all__"


class ReporteIncidenciaPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteIncidenciaPersonal
        fields = "__all__"


class UsuarioAguaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioAgua
        fields = "__all__"


class LicenciaAguaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenciaAgua
        fields = "__all__"
