from django.test import SimpleTestCase


class ConexionEquipoBiometricoImportsTest(SimpleTestCase):
    def test_conexion_equipo_biometrico_imports(self):
        from apps.conexion_equipo_biometrico.services import (
            BiometricConnectionError,
            probe_device_connection,
            read_attendance_logs,
            read_device_capacity,
        )
        from apps.conexion_equipo_biometrico.services.notifications import (
            build_missing_mark_notifications,
        )

        self.assertIsNotNone(BiometricConnectionError)
        self.assertTrue(callable(probe_device_connection))
        self.assertTrue(callable(read_attendance_logs))
        self.assertTrue(callable(read_device_capacity))
        self.assertTrue(callable(build_missing_mark_notifications))
