from django.test import SimpleTestCase


class AsistenciaDiariaImportsTest(SimpleTestCase):
    def test_asistencia_diaria_imports(self):
        from apps.asistencia_diaria.api.views import AsistenciaDiariaViewSet
        from apps.asistencia_diaria.models import AsistenciaDiaria
        from apps.asistencia_diaria.selectors import (
            filter_asistencia_diaria_queryset,
            get_asistencia_diaria_queryset,
        )
        from apps.asistencia_diaria.serializers import AsistenciaDiariaSerializer

        self.assertIsNotNone(AsistenciaDiaria)
        self.assertIsNotNone(AsistenciaDiariaSerializer)
        self.assertIsNotNone(AsistenciaDiariaViewSet)
        self.assertIsNotNone(filter_asistencia_diaria_queryset)
        self.assertIsNotNone(get_asistencia_diaria_queryset)
