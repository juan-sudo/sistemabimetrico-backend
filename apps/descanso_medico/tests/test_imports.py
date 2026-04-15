from django.test import SimpleTestCase


class DescansoMedicoImportsTest(SimpleTestCase):
    def test_descanso_medico_imports(self):
        from apps.descanso_medico.models import DescansoMedico
        from apps.descanso_medico.api.views import DescansoMedicoViewSet

        self.assertIsNotNone(DescansoMedico)
        self.assertIsNotNone(DescansoMedicoViewSet)
