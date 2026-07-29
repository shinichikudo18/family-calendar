from django.apps import AppConfig


class AccountsConfig(AppConfig):
    def ready(self):
        import accounts.signals
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Cuentas y Familias'
