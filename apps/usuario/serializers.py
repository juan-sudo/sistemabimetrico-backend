from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.usuario.models import UsuarioModuloPermiso
from apps.usuario.services import build_usuario_nombre, build_usuario_rol


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    module_permissions = serializers.SerializerMethodField(read_only=True)
    module_permissions_input = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    nombre_completo = serializers.SerializerMethodField(read_only=True)
    rol = serializers.SerializerMethodField(read_only=True)
    modulos_visibles = serializers.SerializerMethodField(read_only=True)

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

    def get_nombre_completo(self, obj):
        return build_usuario_nombre(obj)

    def get_rol(self, obj):
        return build_usuario_rol(obj)

    def get_modulos_visibles(self, obj):
        return sum(1 for item in obj.module_permissions.all() if item.puede_ver)

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
            "nombre_completo",
            "rol",
            "is_staff",
            "is_active",
            "is_superuser",
            "modulos_visibles",
            "password",
            "module_permissions",
            "module_permissions_input",
        )
