from django.test import SimpleTestCase


class PersonalImportsTest(SimpleTestCase):
    def test_personal_imports(self):
        from apps.personal.models.personal import Personal
        from apps.personal.selectors import filter_personal_queryset, get_personal_queryset
        from apps.personal.services import format_ubicacion_label
        from apps.personal.api.urls import urlpatterns

        self.assertIsNotNone(Personal)
        self.assertIsNotNone(filter_personal_queryset)
        self.assertIsNotNone(get_personal_queryset)
        self.assertIsNotNone(format_ubicacion_label)
        self.assertTrue(urlpatterns)
