from django.test import SimpleTestCase


class TurnosImportsTest(SimpleTestCase):
    def test_turnos_imports(self):
        from apps.turnos.models import Turno
        from apps.turnos.api.views import TurnoViewSet
        from apps.turnos.selectors import (
            filter_personal_turno_queryset,
            filter_turno_bloque_queryset,
            filter_turno_queryset,
            get_personal_turno_queryset,
            get_turno_bloque_queryset,
            get_turno_queryset,
        )
        from apps.turnos.services import build_turno_label, format_turno_horario

        self.assertIsNotNone(Turno)
        self.assertIsNotNone(TurnoViewSet)
        self.assertIsNotNone(filter_turno_queryset)
        self.assertIsNotNone(filter_turno_bloque_queryset)
        self.assertIsNotNone(filter_personal_turno_queryset)
        self.assertIsNotNone(get_turno_queryset)
        self.assertIsNotNone(get_turno_bloque_queryset)
        self.assertIsNotNone(get_personal_turno_queryset)
        self.assertIsNotNone(build_turno_label)
        self.assertIsNotNone(format_turno_horario)
