from django.test import SimpleTestCase


class AccountsImportsTest(SimpleTestCase):
    def test_accounts_api_imports(self):
        from apps.accounts.api.views import LoginView, MeView, UsuarioViewSet

        self.assertIsNotNone(LoginView)
        self.assertIsNotNone(MeView)
        self.assertIsNotNone(UsuarioViewSet)
