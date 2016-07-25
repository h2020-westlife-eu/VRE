# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from .base import SettingsBase


class SettingsJenkins(SettingsBase):
    DEBUG = False
    PRODUCTION = False

    DB_NAME = 'pype_webapp'

    BASE_URL = 'http://127.0.0.1:8000'