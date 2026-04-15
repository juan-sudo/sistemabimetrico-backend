from django.test import SimpleTestCase


class TipoDocumentoImportsTest(SimpleTestCase):
    def test_tipo_documento_domain_imports(self):
        from apps.tipo_documento.models import TipoDocumento
        from apps.tipo_documento.api.urls import urlpatterns
        from apps.tipo_documento.selectors import filter_tipo_documento_queryset, get_tipo_documento_queryset
        from apps.tipo_documento.services import build_tipo_documento_label

        self.assertIsNotNone(TipoDocumento)
        self.assertIsNotNone(filter_tipo_documento_queryset)
        self.assertIsNotNone(get_tipo_documento_queryset)
        self.assertIsNotNone(build_tipo_documento_label)
        self.assertTrue(urlpatterns)
