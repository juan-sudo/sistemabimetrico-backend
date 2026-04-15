from django.test import SimpleTestCase


class ReporteAsistenciaDiariaImportsTest(SimpleTestCase):
    def test_reporte_asistencia_diaria_imports(self):
        from apps.reporte_asistencia_diaria.models import ReporteAsistenciaDiaria
        from apps.reporte_asistencia_diaria.api.views import ReporteAsistenciaDiariaViewSet
        from apps.reporte_asistencia_diaria.selectors import (
            filter_reporte_asistencia_diaria_queryset,
            get_reporte_asistencia_diaria_queryset,
        )
        from apps.reporte_asistencia_diaria.services import build_periodo_label, format_time_value

        self.assertIsNotNone(ReporteAsistenciaDiaria)
        self.assertIsNotNone(ReporteAsistenciaDiariaViewSet)
        self.assertIsNotNone(filter_reporte_asistencia_diaria_queryset)
        self.assertIsNotNone(get_reporte_asistencia_diaria_queryset)
        self.assertIsNotNone(build_periodo_label)
        self.assertIsNotNone(format_time_value)
