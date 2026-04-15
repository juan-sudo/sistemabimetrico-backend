from django.test import SimpleTestCase


class UsuarioImportsTest(SimpleTestCase):
    def test_usuario_imports(self):
        from apps.usuario.models import UsuarioModuloPermiso
        from apps.usuario.api.views import UsuarioViewSet
        from apps.usuario.selectors import filter_usuario_queryset, get_usuario_queryset
        from apps.usuario.services import build_usuario_nombre, build_usuario_rol

        self.assertIsNotNone(UsuarioModuloPermiso)
        self.assertIsNotNone(UsuarioViewSet)
        self.assertIsNotNone(filter_usuario_queryset)
        self.assertIsNotNone(get_usuario_queryset)
        self.assertIsNotNone(build_usuario_nombre)
        self.assertIsNotNone(build_usuario_rol)
