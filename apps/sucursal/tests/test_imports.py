from django.test import SimpleTestCase


class SucursalImportsTest(SimpleTestCase):
    def test_sucursal_imports(self):
        from apps.sucursal.models import Sucursal
        from apps.sucursal.api.urls import urlpatterns
        from apps.sucursal.selectors import filter_sucursal_queryset, get_sucursal_queryset
        from apps.sucursal.services import build_sucursal_label

        self.assertIsNotNone(Sucursal)
        self.assertIsNotNone(filter_sucursal_queryset)
        self.assertIsNotNone(get_sucursal_queryset)
        self.assertIsNotNone(build_sucursal_label)
        self.assertTrue(urlpatterns)
