from django.test import SimpleTestCase


class DispositivoImportsTest(SimpleTestCase):
    def test_dispositivo_imports(self):
        from apps.dispositivo.models import Dispositivo
        from apps.dispositivo.api.urls import urlpatterns

        self.assertIsNotNone(Dispositivo)
        self.assertTrue(urlpatterns)
