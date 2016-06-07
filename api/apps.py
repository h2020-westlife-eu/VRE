# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = 'api'

    def ready(self):
        import api.signals.handlers
