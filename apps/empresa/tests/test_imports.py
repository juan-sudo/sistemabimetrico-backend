from django.test import SimpleTestCase


class EmpresaImportsTest(SimpleTestCase):
    def test_empresa_domain_imports(self):
        from apps.empresa.models import Empresa
        from apps.empresa.api.urls import urlpatterns

        self.assertIsNotNone(Empresa)
        self.assertTrue(urlpatterns)
