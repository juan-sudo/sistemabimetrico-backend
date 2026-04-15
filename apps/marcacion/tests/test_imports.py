from django.test import SimpleTestCase


class MarcacionImportsTest(SimpleTestCase):
    def test_marcacion_imports(self):
        from apps.marcacion.models import Marcacion
        from apps.marcacion.views import MarcacionViewSet

        self.assertIsNotNone(Marcacion)
        self.assertIsNotNone(MarcacionViewSet)
