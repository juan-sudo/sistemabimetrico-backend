from django.test import SimpleTestCase


class AreaImportsTest(SimpleTestCase):
    def test_area_imports(self):
        from apps.area.models import Area
        from apps.area.api.urls import urlpatterns

        self.assertIsNotNone(Area)
        self.assertTrue(urlpatterns)
