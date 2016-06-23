# coding: utf-8

# Copyright Luna Technology 2015

from .base import SettingsBase


class SettingsDev(SettingsBase):
    DEBUG = True

    DB_NAME = 'pype'
    DB_USER = 'pype'
    DB_PASS = 'pype'

    BASE_URL = 'http://192.168.56.102:8000'

    def JS_CONFIG(self):
        conf = super(SettingsDev, self).JS_CONFIG()
        conf['WS_SERVER'] = 'http://192.168.56.102:22000/ws'
        conf['ENABLE_REGISTER'] = True
        return conf
