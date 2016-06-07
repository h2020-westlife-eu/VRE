# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from django.conf import settings


def pytest_configure(config):
    setattr(settings, 'BROKER_BACKEND', 'memory')
