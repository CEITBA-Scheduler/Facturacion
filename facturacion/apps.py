from __future__ import unicode_literals

from django.apps import AppConfig


class FacturacionConfig(AppConfig):
    name = 'facturacion'
    verbose_name = 'Facturación'

    def ready(self):
        import facturacion.signals
