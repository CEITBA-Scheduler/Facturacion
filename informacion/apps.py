from django.apps import AppConfig


class InformacionConfig(AppConfig):
    name = 'informacion'
    verbose_name = 'Información'

    def ready(self):
        import informacion.signals
