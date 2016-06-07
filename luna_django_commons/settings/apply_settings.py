# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


import os

from django.core.exceptions import ImproperlyConfigured

import cbs


def apply_settings(vars):
    MODE = os.environ.get('DJANGO_MODE', None)

    if MODE is None:
        raise ImproperlyConfigured('Environment variable DJANGO_MODE is not set')

    cbs.apply('Settings%s' % MODE, vars)
