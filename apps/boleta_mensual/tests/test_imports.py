from django.test import SimpleTestCase


class BoletaMensualImportsTest(SimpleTestCase):
    def test_boleta_mensual_imports(self):
        from apps.boleta_mensual.models import BoletaMensual
        from apps.boleta_mensual.api.views import BoletaMensualViewSet

        self.assertIsNotNone(BoletaMensual)
        self.assertIsNotNone(BoletaMensualViewSet)
