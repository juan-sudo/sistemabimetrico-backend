from django.test import SimpleTestCase


class TipoTrabajadorImportsTest(SimpleTestCase):
    def test_tipo_trabajador_domain_imports(self):
        from apps.tipo_trabajador.models import TipoTrabajador
        from apps.tipo_trabajador.api.urls import urlpatterns
        from apps.tipo_trabajador.selectors import filter_tipo_trabajador_queryset, get_tipo_trabajador_queryset
        from apps.tipo_trabajador.services import build_tipo_trabajador_label

        self.assertIsNotNone(TipoTrabajador)
        self.assertIsNotNone(filter_tipo_trabajador_queryset)
        self.assertIsNotNone(get_tipo_trabajador_queryset)
        self.assertIsNotNone(build_tipo_trabajador_label)
        self.assertTrue(urlpatterns)
