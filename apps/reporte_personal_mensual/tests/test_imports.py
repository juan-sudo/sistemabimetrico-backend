from django.test import SimpleTestCase


class ReportePersonalMensualImportsTest(SimpleTestCase):
    def test_reporte_personal_mensual_imports(self):
        from apps.reporte_personal_mensual.models import ReportePersonalMensual
        from apps.reporte_personal_mensual.api.views import ReportePersonalMensualViewSet
        from apps.reporte_personal_mensual.selectors import (
            filter_reporte_personal_mensual_queryset,
            get_reporte_personal_mensual_queryset,
        )
        from apps.reporte_personal_mensual.services import build_periodo_label, build_resumen_label

        self.assertIsNotNone(ReportePersonalMensual)
        self.assertIsNotNone(ReportePersonalMensualViewSet)
        self.assertIsNotNone(filter_reporte_personal_mensual_queryset)
        self.assertIsNotNone(get_reporte_personal_mensual_queryset)
        self.assertIsNotNone(build_periodo_label)
        self.assertIsNotNone(build_resumen_label)
