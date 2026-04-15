from django.test import SimpleTestCase


class ReporteIncidenciaPersonalImportsTest(SimpleTestCase):
    def test_reporte_incidencia_personal_imports(self):
        from apps.reporte_incidencia_personal.models import ReporteIncidenciaPersonal
        from apps.reporte_incidencia_personal.api.views import ReporteIncidenciaPersonalViewSet
        from apps.reporte_incidencia_personal.selectors import (
            filter_reporte_incidencia_personal_queryset,
            get_reporte_incidencia_personal_queryset,
        )
        from apps.reporte_incidencia_personal.services import build_periodo_label, build_rango_label

        self.assertIsNotNone(ReporteIncidenciaPersonal)
        self.assertIsNotNone(ReporteIncidenciaPersonalViewSet)
        self.assertIsNotNone(filter_reporte_incidencia_personal_queryset)
        self.assertIsNotNone(get_reporte_incidencia_personal_queryset)
        self.assertIsNotNone(build_periodo_label)
        self.assertIsNotNone(build_rango_label)
