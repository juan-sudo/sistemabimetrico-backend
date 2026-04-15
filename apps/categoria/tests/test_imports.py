from django.test import SimpleTestCase


class CategoriaImportsTest(SimpleTestCase):
    def test_categoria_domain_imports(self):
        from apps.categoria.models import Categoria
        from apps.categoria.api.urls import urlpatterns

        self.assertIsNotNone(Categoria)
        self.assertTrue(urlpatterns)
