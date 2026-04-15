from django.test import SimpleTestCase


class BoletaConceptoImportsTest(SimpleTestCase):
    def test_boleta_concepto_imports(self):
        from apps.boleta_concepto.models import BoletaConcepto
        from apps.boleta_concepto.api.views import BoletaConceptoViewSet

        self.assertIsNotNone(BoletaConcepto)
        self.assertIsNotNone(BoletaConceptoViewSet)
