from django.test import SimpleTestCase


class TipoSindicatoImportsTest(SimpleTestCase):
    def test_tipo_sindicato_domain_imports(self):
        from apps.tipo_sindicato.models import TipoSindicato
        from apps.tipo_sindicato.api.urls import urlpatterns
        from apps.tipo_sindicato.selectors import filter_tipo_sindicato_queryset, get_tipo_sindicato_queryset
        from apps.tipo_sindicato.services import build_tipo_sindicato_label

        self.assertIsNotNone(TipoSindicato)
        self.assertIsNotNone(filter_tipo_sindicato_queryset)
        self.assertIsNotNone(get_tipo_sindicato_queryset)
        self.assertIsNotNone(build_tipo_sindicato_label)
        self.assertTrue(urlpatterns)
