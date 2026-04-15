from django.test import SimpleTestCase
from django.urls import reverse


class ReportesSmokeTest(SimpleTestCase):
    def test_health_and_auth_routes_exist(self):
        self.assertEqual(reverse("health-check"), "/api/health/")
        self.assertEqual(reverse("auth-login"), "/api/auth/login/")

    def test_reportes_routes_exist(self):
        self.assertEqual(reverse("reportes-personal-list"), "/api/reportes-personal/")
        self.assertEqual(reverse("reportes-asistencia-diaria-list"), "/api/reportes-asistencia-diaria/")
        self.assertEqual(reverse("reportes-conceptos-list"), "/api/reportes-conceptos/")
        self.assertEqual(reverse("reportes-incidencias-list"), "/api/reportes-incidencias/")

    def test_reportes_module_imports(self):
        from apps.reportes.selectors import (
            get_personal_reporte_base_queryset,
            get_reporte_asistencia_queryset,
            get_reporte_conceptos_queryset,
            get_reporte_incidencias_queryset,
            get_reporte_personal_queryset,
        )
        from apps.reportes.services import build_boleta_detalle, build_reporte_general_payload, sync_reporte_general

        self.assertIsNotNone(get_personal_reporte_base_queryset)
        self.assertIsNotNone(get_reporte_personal_queryset)
        self.assertIsNotNone(get_reporte_asistencia_queryset)
        self.assertIsNotNone(get_reporte_conceptos_queryset)
        self.assertIsNotNone(get_reporte_incidencias_queryset)
        self.assertIsNotNone(build_boleta_detalle)
        self.assertIsNotNone(build_reporte_general_payload)
        self.assertIsNotNone(sync_reporte_general)
