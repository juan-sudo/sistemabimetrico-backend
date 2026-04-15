from django.test import SimpleTestCase


class ReporteConceptoPersonalImportsTest(SimpleTestCase):
    def test_reporte_concepto_personal_imports(self):
        from apps.reporte_concepto_personal.models import ReporteConceptoPersonal
        from apps.reporte_concepto_personal.api.views import ReporteConceptoPersonalViewSet
        from apps.reporte_concepto_personal.selectors import (
            filter_reporte_concepto_personal_queryset,
            get_reporte_concepto_personal_queryset,
        )
        from apps.reporte_concepto_personal.services import build_periodo_label

        self.assertIsNotNone(ReporteConceptoPersonal)
        self.assertIsNotNone(ReporteConceptoPersonalViewSet)
        self.assertIsNotNone(filter_reporte_concepto_personal_queryset)
        self.assertIsNotNone(get_reporte_concepto_personal_queryset)
        self.assertIsNotNone(build_periodo_label)
