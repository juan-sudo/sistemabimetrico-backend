from django.test import SimpleTestCase


class JustificacionImportsTest(SimpleTestCase):
    def test_justificacion_imports(self):
        from apps.justificacion.models import Justificacion
        from apps.justificacion.views import JustificacionViewSet

        self.assertIsNotNone(Justificacion)
        self.assertIsNotNone(JustificacionViewSet)
