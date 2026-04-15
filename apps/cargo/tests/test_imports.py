from django.test import SimpleTestCase


class CargoImportsTest(SimpleTestCase):
    def test_cargo_domain_imports(self):
        from apps.cargo.models import Cargo
        from apps.cargo.api.urls import urlpatterns

        self.assertIsNotNone(Cargo)
        self.assertTrue(urlpatterns)
